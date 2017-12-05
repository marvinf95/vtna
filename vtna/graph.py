__all__ = ['TemporalGraph', 'Graph', 'TemporalNode', 'Edge']

import typing as typ

import vtna.data_import as dimp

# Type Alias
AttributeValue = typ.Union[str, float]


class TemporalGraph(object):
    def __init__(self, edge_table: dimp.TemporalEdgeTable, meta_table: dimp.MetadataTable, granularity: int):
        """
        Creates graphs for all timestamps with a given granularity.

        Args:
            edge_table: Its a table with three columns.
                        The first one specifies a timestamp.
                        And the second and third one specifies the nodes that are interacting at this timestamp.
            meta_table: Its a table with attributes for nodes.
            granularity: Granularity defines the timesteps, for which the different graphs will be created.
        """
        # Create a dictionary with the start and the end of timestamps: key = number of timestep, value = end of timestep
        self.__meta_table = meta_table
        self.__timesteps = {}
        end_interval = edge_table.get_earliest_timestamp() + granularity
        interval_number = 0
        while end_interval < edge_table.get_latest_timestamp():
            self.__timesteps.update({interval_number: end_interval})
            end_interval = end_interval + granularity
            interval_number += 1
        # Add Graph at the last timestamp. The interval could be shorter than the other intervals
        self.__timesteps.update({interval_number: edge_table.get_latest_timestamp()})

        # Create a dictionary that contains the edges for the graphs in the different timesteps
        self.__temporal_edges_graphs = {}
        for key, value in self.__timesteps.items():
            __temp_edge_table = list(edge_table[(value - granularity):value])
            __temp_edge_table = [(t[1], t[2], t[0]) for t in __temp_edge_table]
            __temp_edge_table = [(t[1], t[0], t[2]) if t[1] < t[0] else (t[0], t[1], t[2]) for t in __temp_edge_table]
            # Check if node1 and node2 are the same. If thats the case, create new element with list of timestamp
            totals = {}
            for node1, node2, timestamp in __temp_edge_table:
                if (node1, node2) not in totals:
                    totals[(node1, node2)] = [timestamp]
                else:
                    totals[(node1, node2)].append(timestamp)
            __temp_edge_table = []
            for k, v in totals.items():
                temp = [k[0],k[1],v]
                __temp_edge_table.append(temp)
            self.__temporal_edges_graphs.update({key: __temp_edge_table})

        # Create a list containing nodes with attributes
        self.__temporal_nodes = []
        for __nodes_with_attributes in self.__meta_table.items():
            self.__temporal_nodes.append(TemporalNode(__nodes_with_attributes[0], __nodes_with_attributes[1]))

    def __getitem__(self, time_step: int) -> 'Graph':
        """Returns the graph at the specified timestep"""
        if not isinstance(time_step, int):
            raise TypeError(f'type {int} expected')
        if time_step < 0 or time_step > len(self.__timesteps):
            raise IndexError(f'Timestep doesnt exist')
        return Graph(self.__temporal_edges_graphs.get(time_step))

    def __iter__(self):
        """Initialises iterator."""
        self.n = 0
        return self

    def __next__(self):
        """Get the next graph with the iterator."""
        if self.n <= len(self.__temporal_edges_graphs):
            self.n += 1
            return Graph(self.__temporal_edges_graphs.get(self.n))
        else:
            raise StopIteration

    def __len__(self):
        """Returns the number of graphs that were created cause of the defined granularity."""
        return len(self.__temporal_edges_graphs)

    def get_nodes(self) -> typ.List['TemporalNode']:
        """Returns all nodes with attributes."""
        return self.__temporal_nodes

    def get_node(self, node_id: int) -> 'TemporalNode':
        """Returns one node defined by node_id."""
        if not isinstance(node_id, int):
            raise TypeError(f'type {int} expected')
        if [item for item in self.__temporal_nodes if item.get_id() == node_id]:
            temp_node, = [item for item in self.__temporal_nodes if item.get_id() == node_id]
            return temp_node
        else:
            raise IndexError(f'node_id doesnt exist')


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
        return self.__edges

    def get_edge(self, node1: int, node2: int) -> 'Edge':
        """Returns one edge of a graph defined by node1 and node2"""
        if not isinstance(node1, int) and not isinstance(node2, int):
            raise TypeError(f'type {int} for node1 and node2 expected')
        if [item for item in self.__edges if item[0] == node1 and item[1] == node2 or item[1] == node1 and item[0] == node2]:
            found_edge, = [item for item in self.__edges if item[0] == node1 and item[1] == node2]
            return Edge(found_edge[0],found_edge[1],found_edge[2])
        else:
            raise IndexError(f'Edge doesnt exist')

class TemporalNode(object):
    def __init__(self, node_id: int, meta_attributes: typ.Dict[str, str]):
        """
        Specifies the nodes of the graph. A temporal node is specified through an node_id
        and a list of global attributes for that node.

        Args:
            node_id: ID of the node.
            meta_attributes: Dictionary of attributes for a node.
        """
        self.__node_id = node_id
        self.__global_attributes = meta_attributes
        self.__local_attributes = {}

    def get_id(self) -> int:
        """ID of the temporal node."""
        return self.__node_id

    def get_global_attribute(self, name: str) -> AttributeValue:
        """
        Global attributes are attributes that don't change over time
        These are defined as key, value pairs.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected')
        if self.__global_attributes[name] != None:
            return self.__global_attributes[name]
        else:
            raise IndexError(f'Global attribute does not exist')

    def get_local_attribute(self, name: str, time_step: int) -> AttributeValue:
        """
        Local attributes are attributes that could change per timestep.
        You could get it with a name and a time_step.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected')
        if not isinstance(time_step, int):
            raise TypeError(f'type {int} for time_step expected')
        # TODO: Exception if time_step not exists
        # TODO: Exception if attribute dont exists
        if self.__local_attributes[name] != None and self.__local_attributes[name][time_step] != None:
            return self.__local_attributes[name][time_step]
        else:
            raise IndexError(f'Name or time_step does not exist')

    def update_global_attribute(self, name: str, value: AttributeValue):
        """
        Update a global attribute or add a new attribute.
        If name is not defined yet, a new attribute gets created.
        Otherwise the value with the given name is overridden.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected')
        if not isinstance(value, (str, int)):
            raise TypeError(f'type {str} or type {int} for value expected')
        self.__global_attributes[name] = value

    def update_local_attribute(self, name: str, values: typ.List[AttributeValue]):
        """
        Update a local attribute or add a new attribute.
        To add or update a attribute a name must be defined as first argument.
        As the second argument a list with values is required.
        In that list, the first element stands for the first timestep, the second for the second timestep and so on.
        """
        if not isinstance(name, str):
            raise TypeError(f'type {str} for name expected')
        if all(isinstance(item, (str,int)) for item in values):
            self.__local_attributes[name] = values
        else:
            raise TypeError(f'elements of values list must be of type {str} or {int}')

    # TODO: Should we add functions get_global_attributes and get_local_attributes?


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
        self.__node1 = node1
        self.__node2 = node2

    def get_incident_nodes(self) -> typ.Tuple[int, int]:
        """Get incident nodes of an edge in form of an tuple(node1, node2)"""
        return (self.__node1, self.__node2)

    def get_count(self) -> int:
        """Counts the occurences of an edge in the specified timestep"""
        return len(self.__time_stamps)

    def get_timestamps(self) -> typ.List[int]:
        """Returns list of timestamps for an edge in the specified timestep"""
        return self.__time_stamps

    # We may add edge measures in the future.
