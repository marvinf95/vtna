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
        self.__timesteps = {}
        end_interval = edge_table.get_earliest_timestamp() + granularity
        interval_number = 0
        while end_interval < edge_table.get_latest_timestamp():
            self.__timesteps.update({interval_number: end_interval})
            end_interval = end_interval + granularity
            interval_number += 1
        # Add Graph at the last timestamp. The interval could be shorter than the other intervals
        self.__timesteps.update({interval_number: edge_table.get_latest_timestamp()})
        #self.__timesteps += 1
        # Create graph for every timestep
        self.__temporal_graphs = {}
        self.__nodes_with_attributes = []
        for node in meta_table.keys():
            node_attributes = meta_table[node]
            for key, value in node_attributes.items():
                self.__nodes_with_attributes.append( (node, {key: value}) )
        graph_nodes = nx.Graph()
        graph_nodes.add_nodes_from(self.__nodes_with_attributes)
        self.__temp_graph = nx.Graph()
        #self.__temp_graph.add_edges_from(edge_table)
        for key, value in self.__timesteps.items():
            #print(self.__temp_graph)
            self.__temp_graph = graph_nodes.copy()
            __temp_edge_table = list(edge_table[(value - granularity):value])
            __temp_edge_table = [(t[1], t[2]) for t in __temp_edge_table]
            self.__temp_graph.add_edges_from(__temp_edge_table)
            # Check if python adds always the new __temp_graph or if it works with pointers and deletes everything
            self.__temporal_graphs.update({key: self.__temp_graph})

    def __getitem__(self, time_step: int) -> 'Graph':
        return self.__temporal_graphs.get[time_step]

    #def __iter__(self) -> Iterable[Graph]:
    #    # TODO: Option to iterate over __temporal_graphs and give back the specified graph
    #    pass

    def __len__(self):
        return len(self.__temporal_graphs)

    def get_nodes(self) -> typ.List['TemporalNode']:
        # TODO: Get nodes out of nodes_with_attributes
        pass

    def get_node(self, node_id: int) -> 'TemporalNode':
        # TODO: get nodes out of nodes_with_attributes
        pass


class Graph(object):
    def __init__(self, edges: typ.List['Edge']):
        self.__edges = edges

    def get_edges(self) -> typ.List['Edge']:
        return self.__edges

    def get_edge(self, node1: int, node2: int) -> 'Edge':
        if [(node1, node2) for node1, node2 in self.__edges]:
            return True
        else:
            return False


class TemporalNode(object):
    def __init__(self, node_id: int, meta_attributes: typ.Dict[str, str]):
        pass

    def get_id(self) -> int:
        pass

    def get_global_attribute(self, name: str) -> AttributeValue:
        pass

    def get_local_attribute(self, name: str, time_step: int) -> AttributeValue:
        pass

    def update_global_attribute(self, name: str, value: AttributeValue):
        pass

    def update_local_attribute(self, name: str, values: typ.List[AttributeValue]):
        pass


class Edge(object):
    def __init__(self, node1: int, node2: int, time_stamps: typ.List[int]):
        pass

    def get_incident_nodes(self) -> typ.Tuple[int, int]:
        pass

    def get_count(self) -> int:
        pass

    def get_timestamps(self) -> typ.List[int]:
        pass

    # We may add edge measures in the future.
