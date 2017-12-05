__all__ = ['TemporalGraph', 'Graph', 'TemporalNode', 'Edge']

import typing as typ
import networkx as nx

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

        self.__temporal_nodes = []
        for __nodes_with_attributes in self.__meta_table.items():
            self.__temporal_nodes.append(TemporalNode(__nodes_with_attributes[0], __nodes_with_attributes[1]))

    def __getitem__(self, time_step: int) -> 'Graph':
        return Graph(self.__temporal_edges_graphs.get(time_step))

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n <= len(self.__temporal_edges_graphs):
            self.n += 1
            return Graph(self.__temporal_edges_graphs.get(self.n))
        else:
            raise StopIteration

    def __len__(self):
        return len(self.__temporal_edges_graphs)

    def get_nodes(self) -> typ.List['TemporalNode']:
        return self.__temporal_nodes

    def get_node(self, node_id: int) -> 'TemporalNode':
        temp_node, = [item for item in self.__temporal_nodes if item.get_id() == node_id]
        return temp_node


class Graph(object):
    def __init__(self, edges: typ.List['Edge']):
        self.__edges = edges

    def get_edges(self) -> typ.List['Edge']:
        return self.__edges

    def get_edge(self, node1: int, node2: int) -> 'Edge':
        if [item for item in self.__edges if item[0] == node1 and item[1] == node2 or item[1] == node1 and item[0] == node2]:
            found_edge, = [item for item in self.__edges if item[0] == node1 and item[1] == node2]
            return Edge(found_edge[0],found_edge[1],found_edge[2])
        else:
            return False


class TemporalNode(object):
    def __init__(self, node_id: int, meta_attributes: typ.Dict[str, str]):
        self.__node_id = node_id
        self.__global_attributes = meta_attributes
        self.__local_attributes = {}

    def get_id(self) -> int:
        return self.__node_id

    def get_global_attribute(self, name: str) -> AttributeValue:
        # TODO: Exception if attribute dont exists
        return self.__global_attributes[name]

    def get_local_attribute(self, name: str, time_step: int) -> AttributeValue:
        # TODO: Exception if time_step not exists
        # TODO: Exception if attribute dont exists
        return self.__local_attributes[name][time_step]

    def update_global_attribute(self, name: str, value: AttributeValue):
        self.__global_attributes[name] = value

    def update_local_attribute(self, name: str, values: typ.List[AttributeValue]):
        self.__local_attributes[name] = values

    # TODO: Should we add functions get_global_attributes and get_local_attributes?


class Edge(object):
    def __init__(self, node1: int, node2: int, time_stamps: typ.List[int]):
        self.__time_stamps = time_stamps
        self.__node1 = node1
        self.__node2 = node2

    def get_incident_nodes(self) -> typ.Tuple[int, int]:
        return (self.__node1, self.__node2)

    def get_count(self) -> int:
        return len(self.__time_stamps)

    def get_timestamps(self) -> typ.List[int]:
        return self.__time_stamps

    # We may add edge measures in the future.
