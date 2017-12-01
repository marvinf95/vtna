__all__ = ['LocalDegreeCentrality', 'GlobalDegreeCentrality']  # Only the actual implementations

import abc
import typing as typ

import vtna.graph
import vtna.utility as util


class NodeMeasure(util.Describable, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, graph: vtna.graph.TemporalGraph):
        if type(graph) != vtna.graph.TemporalGraph:
            raise TypeError(f'type {vtna.graph.TemporalGraph} expected, received type {type(graph)}')

    @abc.abstractmethod
    def add_to_graph(self):
        """Adds already calculated measures to nodes as attributes."""
        pass

    @abc.abstractmethod
    def __getitem__(self, node_id: int):
        if type(node_id) != int:
            raise TypeError(f'type {int} expected, received type {type(node_id)}')

# Other than computation, most functionality can be implemented in the abstract classes LocalNodeMeasure
# and GlobalNodeMeasure


class LocalNodeMeasure(NodeMeasure, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __getitem__(self, node_id: int) -> typ.Dict[int, float]:
        """Returns list of timestep measures for node node_id"""
        return super().__getitem__(node_id)


class GlobalNodeMeasure(NodeMeasure, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __getitem__(self, node_id: int) -> float:
        """Returns global measure for node node_id"""
        return super().__getitem__(node_id)


# Implementations


class LocalDegreeCentrality(LocalNodeMeasure):

    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self.temporal_graph = graph
        self.degree_centrality_dict = []
        for node in self.temporal_graph.get_nodes():
            node_dc = []
            time = 0
            for localGraph in self.temporal_graph:
                if not node_dc[time]:
                    node_dc[time] = 0
                for edge in localGraph.get_edges():
                    if node.get_id() in edge.get_incident_nodes():
                        node_dc[time] += edge.get_count()
                time += 1
            self.degree_centrality_dict[node.get_id()] = node_dc

    def get_name(self) -> str:
        return "Local Degree Centrality"

    def get_description(self) -> str:
        return "Calculates node degree for every node"

    def add_to_graph(self):
        for node in self.temporal_graph.get_nodes():
            node.update_local_attribute(self.get_name(), self.degree_centrality_dict[node.get_id()])

    def __getitem__(self, node_id: int) -> typ.Dict[int, float]:
        super().__getitem__(node_id)
        return self.degree_centrality_dict[node_id]


class GlobalDegreeCentrality(GlobalNodeMeasure):

    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self.temporal_graph = graph
        self.degree_centrality = dict()
        local_dc = LocalDegreeCentrality(graph)
        for node in graph.get_nodes():
            nid = node.get_id()
            self.degree_centrality[nid] = sum(local_dc[nid])

    def get_name(self) -> str:
        return "Global Degree Centrality"

    def get_description(self) -> str:
        return "Calculates degree for every node, which is the sum of all local degrees"

    def add_to_graph(self):
        for node in self.temporal_graph.get_nodes():
            node.update_global_attribute(self.get_name(), self.degree_centrality[node.get_id()])

    def __getitem__(self, node_id: int) -> float:
        super().__getitem__(node_id)
        return self.degree_centrality[node_id]
