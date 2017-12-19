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
        """
        self.__graphs = list()  # type: typ.List[Graph]
        self.__nodes = dict()  # type: typ.Dict[int, TemporalNode]

        buckets = dimp.group_edges_by_granularity(edges, granularity)
        # Create graphs
        for time_step, edges in enumerate(buckets):
            edge_timestamps = col.defaultdict(list)
            for timestamp, node1, node2 in edges:
                node1, node2 = sorted((node1, node2))
                edge_timestamps[(node1, node2)].append(timestamp)
            edges = [Edge(edge[0], edge[1], timestamps) for edge, timestamps in edge_timestamps.items()]
            self.__graphs.append(Graph(edges))
        # Create nodes
        if meta_table is not None:
            for node_id, attributes in meta_table.items():
                self.__nodes[node_id] = TemporalNode(node_id, attributes, len(buckets))
        else:
            nodes = set()
            for g in self.__graphs:
                for e in g.get_edges():
                    nodes.update(e.get_incident_nodes())
            self.__nodes = dict((node_id, TemporalNode(node_id, dict(), len(buckets)))
                                for node_id in nodes)

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

    def get_nodes(self) -> typ.List['TemporalNode']:
        """Returns all nodes with attributes."""
        return list(self.__nodes.values())

    def get_node(self, node_id: int) -> 'TemporalNode':
        """Returns one node defined by node_id."""
        return self.__nodes[node_id]


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
        """Get incident nodes of an edge in form of an tuple(node1, node2)"""
        return self.__node1, self.__node2

    def get_count(self) -> int:
        """Counts the occurences of an edge in the specified timestep"""
        return len(self.__time_stamps)

    def get_timestamps(self) -> typ.List[int]:
        """Returns list of timestamps for an edge in the specified timestep"""
        return self.__time_stamps.copy()


class InvalidLocalAttributeValuesLength(Exception):
    pass
