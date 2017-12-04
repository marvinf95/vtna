__all__ = ['LocalDegreeCentrality', 'GlobalDegreeCentrality',
           'LocalBetweennessCentrality', 'GlobalBetweennessCentrality',
           'LocalClosenessCentrality', 'GlobalClosenessCentrality']

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
                f'type {vtna.graph.TemporalGraph} expected, received type ' \
                f'{type(graph)}')

    @abc.abstractmethod
    def add_to_graph(self):
        """Adds already calculated measures to nodes as attributes."""
        pass

    @abc.abstractmethod
    def __getitem__(self, node_id: int):
        if type(node_id) != int:
            raise TypeError(
                f'type {int} expected, received type {type(node_id)}')


# Other than computation, most functionality can be implemented in the
# abstract classes LocalNodeMeasure
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


def _add_local_edge_weights(nx_graph: nx.Graph, local_graph: vtna.graph.Graph):
    max_weight = max([edge.get_count() for edge in local_graph.get_edges()])
    for edge in local_graph.get_edges():
        n1 = edge.get_incident_nodes()[0]
        n2 = edge.get_incident_nodes()[1]
        nx_graph.edges[n1, n2]['weight'] = max_weight - edge.get_count()


def _add_global_edge_weights(nx_graph: nx.Graph,
                             local_graph: vtna.graph.TemporalGraph):
    max_weight = max([e['count'] for e in nx_graph.edges()])
    for edge in nx_graph:
        edge['weight'] = max_weight - edge['count']


# Implementations


class LocalDegreeCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph = graph
        self._dc_dict: typ.Dict[
            NodeID, typ.List[float]] = dict()

        for node in self._temporal_graph.get_nodes():
            node_dc = []
            for localGraph in self._temporal_graph:
                node_degree = 0
                for edge in localGraph.get_edges():
                    if node.get_id() in edge.get_incident_nodes():
                        node_degree += edge.get_count()
                node_dc.append(node_degree)
            self._dc_dict[node.get_id()] = node_dc

    def get_name(self) -> str:
        return "Local Degree Centrality"

    def get_description(self) -> str:
        return "Calculates node degree for every node"

    def add_to_graph(self):
        for node in self._temporal_graph.get_nodes():
            node.update_local_attribute(self.get_name(),
                                        self._dc_dict[
                                            node.get_id()])

    def __getitem__(self, node_id: int) -> typ.List[float]:
        super().__getitem__(node_id)
        return self._dc_dict[node_id]


class GlobalDegreeCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph = graph
        self._dc_dict = dict()
        local_dc = LocalDegreeCentrality(graph)
        for node in graph.get_nodes():
            self._dc_dict[node.get_id()] = sum(local_dc[node.get_id()])

    def get_name(self) -> str:
        return "Global Degree Centrality"

    def get_description(self) -> str:
        return "Calculates degree for every node, which is the sum of all " \
               "local degrees"

    def add_to_graph(self):
        for node in self._temporal_graph.get_nodes():
            node.update_global_attribute(self.get_name(),
                                         self._dc_dict[node.get_id()])

    def __getitem__(self, node_id: int) -> float:
        super().__getitem__(node_id)
        return self._dc_dict[node_id]


class LocalBetweennessCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph = graph
        self._bc_dict: typ.Dict[NodeID, typ.List[float]] = dict()

        # Initialize empty lists for every node, because not every node
        # exists in every local graph
        for node in self._temporal_graph.get_nodes():
            if node.get_id() not in self._bc_dict:
                self._bc_dict[node.get_id()] = len(self._temporal_graph) * [0]
        # We also have to use an index because appending won't work with
        # nodes missing in some local graphs
        timestep = 0
        for local_graph in self._temporal_graph:
            nx_graph = util.graph2networkx(local_graph)
            _add_local_edge_weights(nx_graph, local_graph)
            # TODO: Should this be normalized? NetworkX default is True
            for (node_id, bc) in nx.betweenness_centrality(nx_graph,
                                                           normalized=True,
                                                           weight='weight'):
                self._bc_dict[node_id][timestep] = bc
            timestep += 1

    def get_name(self) -> str:
        return "Local Betweenness Centrality"

    def get_description(self) -> str:
        return "Calculates Betweenness Centrality of each node, defined by " \
               "amount of shortest paths in the local graph through this " \
               "node."

    def __getitem__(self, node_id: int) -> typ.List[float]:
        return self._bc_dict[node_id]

    def add_to_graph(self):
        for (node_id, time_cent_list) in self._bc_dict:
            self._temporal_graph.get_node(node_id).update_local_attribute(
                self.get_name(), time_cent_list)


class GlobalBetweennessCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph = graph
        self._bc_dict: typ.Dict[NodeID, float]

        nx_graph = util.temporal_graph2networkx(self._temporal_graph)
        _add_global_edge_weights(nx_graph, self._temporal_graph)
        # TODO: Should this be normalized? NetworkX default is True
        self._bc_dict = nx.betweenness_centrality(nx_graph, normalized=True,
                                                  weight='weight')

    def get_name(self) -> str:
        return "Global Betweenness Centrality"

    def get_description(self) -> str:
        return "Calculates Betweenness Centrality of each node, defined by " \
               "amount of shortest paths in the global graph through this " \
               "node."

    def __getitem__(self, node_id: int) -> float:
        return self._bc_dict[node_id]

    def add_to_graph(self):
        for (node_id, bc) in self._bc_dict:
            self._temporal_graph.get_node(node_id).update_global_attribute(
                self.get_name(), bc)


class LocalClosenessCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph = graph
        self._cc_dict: typ.Dict[NodeID, typ.List[float]] = dict()

        # Initialize empty lists for every node, because not every node
        # exists in every local graph
        for node in self._temporal_graph.get_nodes():
            if node.get_id() not in self._cc_dict:
                self._cc_dict[node.get_id()] = len(self._temporal_graph) * [0]
        # We also have to use an index because appending won't work with
        # nodes missing in some local graphs
        timestep = 0
        for local_graph in self._temporal_graph:
            nx_graph = util.graph2networkx(local_graph)
            _add_local_edge_weights(nx_graph, local_graph)
            for (node_id, bc) in nx.closeness_centrality(nx_graph,
                                                         distance='weight'):
                self._cc_dict[node_id][timestep] = bc
            timestep += 1

    def get_name(self) -> str:
        return "Local Closeness Centrality"

    def get_description(self) -> str:
        return "Calculates Closeness Centrality of each node, defined by " \
               "the sum of the length of the shortest paths in the local " \
               "graph through this node."

    def __getitem__(self, node_id: int) -> typ.List[float]:
        return self._cc_dict[node_id]

    def add_to_graph(self):
        for (node_id, time_cent_list) in self._cc_dict:
            self._temporal_graph.get_node(node_id).update_local_attribute(
                self.get_name(), time_cent_list)


class GlobalClosenessCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph = graph
        self._bc_dict: typ.Dict[NodeID, float]

        nx_graph = util.temporal_graph2networkx(self._temporal_graph)
        _add_global_edge_weights(nx_graph, self._temporal_graph)
        self._bc_dict = nx.closeness_centrality(nx_graph, distance='weight')

    def get_name(self) -> str:
        return "Global Closeness Centrality"

    def get_description(self) -> str:
        return "Calculates Closeness Centrality of each node, defined by " \
               "the sum of the length of the shortest paths in the global " \
               "graph through this node."

    def __getitem__(self, node_id: int) -> float:
        return self._bc_dict[node_id]

    def add_to_graph(self):
        for (node_id, bc) in self._bc_dict:
            self._temporal_graph.get_node(node_id).update_global_attribute(
                self.get_name(), bc)
