__all__ = ['LocalDegreeCentrality',
           'GlobalDegreeCentrality', 'LocalBetweennessCentrality', 'GlobalBetweennessCentrality']  # Only the actual implementations

import abc
import typing as typ

import vtna.graph
import vtna.utility as util

import networkx as nx

# Type aliases
NodeID = int
Timestep = int


class NodeMeasure(util.Describable, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, graph: vtna.graph.TemporalGraph):
        if type(graph) != vtna.graph.TemporalGraph:
            raise TypeError(
                f'type {vtna.graph.TemporalGraph} expected, received type {type(graph)}')

    @abc.abstractmethod
    def add_to_graph(self):
        """Adds already calculated measures to nodes as attributes."""
        pass

    @abc.abstractmethod
    def __getitem__(self, node_id: int):
        if type(node_id) != int:
            raise TypeError(
                f'type {int} expected, received type {type(node_id)}')


# Other than computation, most functionality can be implemented in the abstract classes LocalNodeMeasure
# and GlobalNodeMeasure


class LocalNodeMeasure(NodeMeasure, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __getitem__(self, node_id: int) -> typ.List[float]:
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
        self.degree_centrality_dict: typ.Dict[NodeID, typ.List[float]] = dict()

        for node in self.temporal_graph.get_nodes():
            node_dc = []
            for localGraph in self.temporal_graph:
                node_degree = 0
                for edge in localGraph.get_edges():
                    if node.get_id() in edge.get_incident_nodes():
                        node_degree += edge.get_count()
                node_dc.append(node_degree)
            self.degree_centrality_dict[node.get_id()] = node_dc

    def get_name(self) -> str:
        return "Local Degree Centrality"

    def get_description(self) -> str:
        return "Calculates node degree for every node"

    def add_to_graph(self):
        for node in self.temporal_graph.get_nodes():
            node.update_local_attribute(self.get_name(),
                                        self.degree_centrality_dict[
                                            node.get_id()])

    def __getitem__(self, node_id: int) -> typ.List[float]:
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
            node.update_global_attribute(self.get_name(),
                                         self.degree_centrality[node.get_id()])

    def __getitem__(self, node_id: int) -> float:
        super().__getitem__(node_id)
        return self.degree_centrality[node_id]


class LocalBetweennessCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self.temporal_graph = graph
        self.bc_dict: typ.Dict[NodeID, typ.List[float]] = dict()

        # Initialize empty lists for every node, because not every node
        # exists in every local graph
        for node in self.temporal_graph.get_nodes():
            if node.get_id() not in self.bc_dict:
                self.bc_dict[node.get_id()] = len(self.temporal_graph)*[0]
        # We also have to use an index because appending won't work with
        # nodes missing in some local graphs
        timestep = 0
        for local_graph in self.temporal_graph:
            nx_graph = util.graph2networkx(local_graph)
            # TODO: Should this be normalized? NetworkX default is True
            # TODO: Additional measure that accounts for edge weights?
            for (node_id, bc) in nx.betweenness_centrality(nx_graph,
                                                     normalized=True):
                self.bc_dict[node_id][timestep] = bc
            timestep += 1

    def get_name(self) -> str:
        return "Local Betweenness Centrality"

    def get_description(self) -> str:
        return "Calculates Betweenness Centrality of each node, defined by " \
                "amount of shortest paths in the local graph through this " \
               "node."

    def __getitem__(self, node_id: int) -> typ.List[float]:
        return self.bc_dict[node_id]

    def add_to_graph(self):
        for (node_id, time_cent_list) in self.bc_dict:
            self.temporal_graph.get_node(node_id).update_local_attribute(
                self.get_name(), time_cent_list)


class GlobalBetweennessCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        pass

    def get_name(self) -> str:
        return "Global Betweenness Centrality"

    def get_description(self) -> str:
        return "Calculates Betweenness Centrality of each node, defined by " \
                "amount of shortest paths in the global graph through this " \
               "node."

    def __getitem__(self, node_id: int) -> float:
        pass

    def add_to_graph(self):
        pass
