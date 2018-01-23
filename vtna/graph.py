__all__ = ['TemporalGraph', 'Graph', 'TemporalNode', 'Edge']

import collections as col
import typing as typ

import vtna.data_import as dimp

# Type Alias
AttributeValue = typ.Union[str, float]


class TemporalGraph(object):
    def __init__(self, edges: typ.List[dimp.TemporalEdge], meta_table: dimp.MetadataTable, granularity: int):
        """
        Creates graphs for all timestamps with a given granularity.

        Args:
            edges: List of temporal edges. Each edge is a triple (timestamp, node, node).
            meta_table: MetadataTable with static node attributes.
            granularity: Granularity defines the size of time intervals, which will be considered as time steps.
                Each time step has an associated aggregated graph containing all edges occurring in the time interval.
        Raises:
            MissingNodesInMetadataError: Is raised, when a node occurs in the provided edges but does not appear in the
                provided metadata. Can never be raised, if metadata is None.
        """
        self.__graphs = list()  # type: typ.List[Graph]
        self.__nodes = dict()  # type: typ.Dict[int, TemporalNode]
        self.__granularity = granularity
        self.__attributes_info = dict()  # type: typ.Dict[str, typ.Dict[str, str]]
        self.__metadata = meta_table

        buckets = dimp.group_edges_by_granularity(edges, granularity)
        n_timesteps = len(buckets)
        # Create graphs
        for time_step, edges in enumerate(buckets):
            edge_timestamps = col.defaultdict(list)
            for timestamp, node1, node2 in edges:
                node1, node2 = sorted((node1, node2))
                edge_timestamps[(node1, node2)].append(timestamp)
            edges = [Edge(edge[0], edge[1], timestamps) for edge, timestamps in edge_timestamps.items()]
            self.__graphs.append(Graph(edges))
        # Collect all node ids.
        node_ids = set()  # type: typ.Set[int]
        for g in self.__graphs:
            for e in g.get_edges():
                node_ids.update(e.get_incident_nodes())
        # Create temporal nodes.
        if meta_table is None:
            self.__nodes = dict((node_id, TemporalNode(node_id, dict(), n_timesteps))
                                for node_id in node_ids)
        else:
            # Add nodes that only exist in metadata
            node_ids.update(meta_table.keys())
            for node_id in node_ids:
                try:
                    attributes = meta_table[node_id]
                except KeyError:
                    raise MissingNodesInMetadataError(node_id)
                self.__nodes[node_id] = TemporalNode(node_id, attributes, n_timesteps)

    def __getitem__(self, time_step: int) -> 'Graph':
        """Returns the graph at the specified timestep"""
        if time_step < 0 or time_step >= len(self.__graphs):
            raise IndexError(f'Index {time_step} out of bounds')
        return self.__graphs[time_step]

    def __iter__(self) -> typ.Iterable['Graph']:
        def __gen():
            for graph in self.__graphs:
                yield graph
        return __gen()

    def __len__(self):
        """Returns the number of graphs that were created cause of the defined granularity."""
        return len(self.__graphs)

    def add_attribute(self, name: str, measurement_type: str, scope: str,
                      attributes: typ.Dict[int, typ.Union[AttributeValue, typ.List[AttributeValue]]] = None,
                      categories: typ.List[str] = None, range: typ.Tuple[float, float] = None):
        """
        Adds local attribute values with name to all nodes in this temporal graph.

        Args:
            name: Name of the attribute
            measurement_type: Which kind of measurement type the values are, can be 'N' for nominal,
                'I' for interval or 'O' for ordinal.
            scope: If this attribute applies to a global or local node, can be either 'global' or 'local'.
            attributes: Dict that maps each node to a list over timesteps of measurement values. If None,
                name and measurement_type will be registered without changing the nodes.
            categories: List of all possible categorical values, if this attribute is nominal/categorical or ordinal.
                If it's ordinal, the categories have to be in their supposed order.
            range: Tuple with minimum and maximum values for interval attributes.
        """
        self.__attributes_info[name] = dict(measurement_type=measurement_type, scope=scope, categories=categories, range=range)
        if attributes is not None:
            for node in self.get_nodes():
                if scope == 'local':
                    node.update_local_attribute(name, attributes[node.get_id()])
                elif scope == 'global':
                    node.update_global_attribute(name, attributes[node.get_id()])

    def get_attributes_info(self) -> typ.Dict[str, typ.Dict[str, typ.Union[str, typ.List[str]]]]:
        attributes = dict()
        # Add metadata attributes with current name
        for attribute_name in self.__metadata.get_attribute_names():
            attributes[attribute_name] = dict(
                measurement_type='O' if self.__metadata.is_ordered(attribute_name) else 'N',
                scope='global',
                categories=self.__metadata.get_categories(attribute_name))
        # Add attributes registered here
        attributes.update(self.__attributes_info)
        return attributes

    def get_nodes(self) -> typ.List['TemporalNode']:
        """Returns all nodes with attributes."""
        return list(self.__nodes.values())

    def get_node(self, node_id: int) -> 'TemporalNode':
        """Returns one node defined by node_id."""
        return self.__nodes[node_id]

    def get_granularity(self) -> int:
        return self.__granularity


class Graph(object):
    def __init__(self, edges: typ.List['Edge']):
        """
        Graph for one timestamp, specified through edges and timestamps for edges.

        Args:
            edges: A list of edges. An edge is of type: Edge(node1, node2, typ.List[int])
                   The list contains the timestamps for that the edge occurs in the graph.
        """
        self.__edges = edges

    def get_edges(self) -> typ.List['Edge']:
        """Returns edge list of graph."""
        return self.__edges.copy()

    def get_edge(self, node1: int, node2: int) -> 'Edge':
        """Returns one edge of a graph defined by node1 and node2"""
        node1, node2 = sorted((node1, node2))
        try:
            edge = [edge for edge in self.__edges if edge.get_incident_nodes() == (node1, node2)][0]
        except IndexError:
            raise KeyError(f'Edge of nodes ({node1}, {node2}) does not exist')
        return edge


class TemporalNode(object):
    def __init__(self, node_id: int, meta_attributes: typ.Dict[str, str], n_timesteps: int):
        """
        Specifies the nodes of the graph. A temporal node is specified through an node_id
        and a list of global attributes for that node.

        Args:
            node_id: ID of the node.
            meta_attributes: Dictionary of attributes for a node.
        """
        self.__node_id = node_id  # type: int
        self.__global_attributes = meta_attributes  # type: typ.Dict[str, AttributeValue]
        self.__local_attributes = {}  # type: typ.Dict[str, typ.List[AttributeValue]]
        self.__n_timesteps = n_timesteps

    def get_id(self) -> int:
        """ID of the temporal node."""
        return self.__node_id

    def get_global_attribute(self, name: str) -> AttributeValue:
        """
        Global attributes are attributes that don't change over time
        These are defined as key, value pairs.
        They also contain metadata associated with this node, retrievable by
        specifying the attribute name as name parameter.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected, received type {type(name)}')
        return self.__global_attributes[name]

    def get_local_attribute(self, name: str, time_step: int) -> AttributeValue:
        """
        Local attributes are attributes that could change per timestep.
        You could get it with a name and a time_step.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected, received type {type(name)}')
        return self.__local_attributes[name][time_step]

    def update_global_attribute(self, name: str, value: AttributeValue):
        """
        Update a global attribute or add a new attribute.
        If name is not defined yet, a new attribute gets created.
        Otherwise the value with the given name is overridden.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected, received type {type(name)}')
        self.__global_attributes[name] = value

    def update_local_attribute(self, name: str, values: typ.List[AttributeValue]):
        """
        Update a local attribute or add a new attribute.
        To add or update a attribute a name must be defined as first argument.
        As the second argument a list with values is required.
        In that list, the first element stands for the first timestep, the second for the second timestep and so on.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected, received type {type(name)}')
        if len(values) != self.__n_timesteps:
            raise InvalidLocalAttributeValuesLength(f'expected values of length {self.__n_timesteps}, '
                                                    f'received length {len(values)}')
        self.__local_attributes[name] = values.copy()


class Edge(object):
    def __init__(self, node1: int, node2: int, time_stamps: typ.List[int]):
        """
        Edge defined through two nodes and timestamps in which the edge occurs.

        Args:
            node1: The first node that describes the edge.
            node2: The second node that describes the edge.
            time_stamps: List of timestamps in which the edge occurs in the specified timestep.
        """
        self.__time_stamps = time_stamps
        self.__node1, self.__node2 = sorted((node1, node2))

    def get_incident_nodes(self) -> typ.Tuple[int, int]:
        """Get ids of incident nodes of an edge in form of an tuple(node1, node2)"""
        return self.__node1, self.__node2

    def get_count(self) -> int:
        """Counts the occurences of an edge in the specified timestep"""
        return len(self.__time_stamps)

    def get_timestamps(self) -> typ.List[int]:
        """Returns list of timestamps for an edge in the specified timestep"""
        return self.__time_stamps.copy()


class InvalidLocalAttributeValuesLength(Exception):
    pass


class MissingNodesInMetadataError(Exception):
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.message = f'Metadata is missing row for node with id {node_id}'
