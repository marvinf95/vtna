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
        return super().__getitem__(node_id)


class GlobalNodeMeasure(NodeMeasure, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __getitem__(self, node_id: int) -> float:
        return super().__getitem__(node_id)


# Implementations


class LocalDegreeCentrality(LocalNodeMeasure):

    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self.temporal_graph = graph
        self.degree_centrality_list = []
        for localGraph in self.temporal_graph:
            degree_centrality = dict()
            for edge in localGraph.get_edges():
                for nid in edge.get_incident_nodes():
                    if nid not in degree_centrality:
                        degree_centrality[nid] = 0
                    degree_centrality[nid] += edge.get_count()
            self.degree_centrality_list.append(degree_centrality)

    def get_name(self) -> str:
        return "Local Degree Centrality"

    def get_description(self) -> str:
        return "Calculates node degree for every node"

    def add_to_graph(self):
        for node in self.temporal_graph.get_nodes():
            node_centralities = [c[node.get_id()] for c in self.degree_centrality_list]
            node.update_local_attribute(self.get_name(), node_centralities)

    def __getitem__(self, node_id: int) -> typ.Dict[int, float]:
        super().__getitem__(node_id)
        return self.degree_centrality_list[node_id]


class GlobalDegreeCentrality(GlobalNodeMeasure):

    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self.temporal_graph = graph
        self.degree_centrality = dict()
        local_dc = LocalDegreeCentrality(graph)
        for node in graph.get_nodes():
            nid = node.get_id()
            self.degree_centrality[nid] = sum([centrality_dict[nid] for centrality_dict in local_dc])

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
