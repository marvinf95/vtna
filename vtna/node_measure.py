__all__ = ['LocalDegreeCentrality', 'GlobalDegreeCentrality',
           'LocalBetweennessCentrality', 'GlobalBetweennessCentrality',
           'LocalClosenessCentrality', 'GlobalClosenessCentrality']

import abc
import typing as typ

import vtna.graph
import vtna.utility as util

import networkx as nx
import numpy as np

# Type aliases
NodeID = int
MeasureValue = float


class NodeMeasure(util.Describable, metaclass=abc.ABCMeta):
    """
    The base class for all node measures. Each node measure makes use of the
    temporal graph, and the values can be applied to it or queried by
    __getitem()__.
    This base class provides only basic checks of invalid parameters.
    """
    @abc.abstractmethod
    def __init__(self, graph: vtna.graph.TemporalGraph):
        if not isinstance(graph, vtna.graph.TemporalGraph):
            raise TypeError(
                f'type {vtna.graph.TemporalGraph} expected, received type {type(graph)}')

    @abc.abstractmethod
    def add_to_graph(self):
        """Adds already calculated measures to nodes as attributes."""
        pass

    @abc.abstractmethod
    def __getitem__(self, node_id: NodeID):
        """Returns some kind of measure information for the provided node."""
        if not isinstance(node_id, (int, np.integer)):
            raise TypeError(
                f'type {NodeID} expected, received type {type(node_id)}')


"""
The following two classes are specifications on local and global measure values.
Because of abstractions that are explained below, variable assignment and
add_to_graph and __getitem__ functionality can already be implemented in 
these base classes.
"""


class LocalNodeMeasure(NodeMeasure, metaclass=abc.ABCMeta):
    """
    A local measure always provides for every node a list of measure values,
    with the index referencing the timestep the measurement applies to.
    Therefore, the methods add_to_graph and __getitem__ can already be
    implemented as default here.
    """
    @abc.abstractmethod
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph: vtna.graph.TemporalGraph = graph
        self._measures_dict: typ.Dict[NodeID, typ.List[MeasureValue]] = {}

    def add_to_graph(self):
        value_range = (min([min(l) for l in self._measures_dict.values()]),
                       max([max(l) for l in self._measures_dict.values()]))
        self._temporal_graph.add_measure_attribute(self.get_name(), 'I', 'local', self._measures_dict, interval_range=value_range)

    def __getitem__(self, node_id: NodeID) -> typ.List[MeasureValue]:
        """Returns list of timestep measures for node node_id"""
        super().__getitem__(node_id)
        return self._measures_dict[node_id]


class GlobalNodeMeasure(NodeMeasure, metaclass=abc.ABCMeta):
    """
    A global measure only provides a single measurement value for each node, but
    add_to_graph and __getitem__ can be generally implemented already as well,
    like the local measures.
    """
    @abc.abstractmethod
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        self._temporal_graph: vtna.graph.TemporalGraph = graph
        self._measures_dict: typ.Dict[NodeID, MeasureValue] = dict((node.get_id(), 0.0)
                                                                   for node in graph.get_nodes())

    def add_to_graph(self):
        value_range = (min(self._measures_dict.values()), max(self._measures_dict.values()))
        self._temporal_graph.add_measure_attribute(self.get_name(), 'I', 'global', attributes=self._measures_dict,
                                                   interval_range=value_range)

    def __getitem__(self, node_id: NodeID) -> MeasureValue:
        """Returns global measure for node node_id"""
        super().__getitem__(node_id)
        return self._measures_dict[node_id]


def _networkx_local_centrality(temporal_graph: vtna.graph.TemporalGraph, nx_centrality_func: typ.Callable) \
        -> typ.Dict[NodeID, typ.List[MeasureValue]]:
    """
    Computes local centralities for a temporal graph based on a networkx centrality function.

    Args:
        temporal_graph: The temporal graph which centralities will be computed
        nx_centrality_func: A wrapper function that takes a networkx graph and
            returns the computed centralities as dictionary.
    """
    centrality_dict: typ.Dict[NodeID, typ.List[MeasureValue]] = dict()
    # Initialize empty lists for every node, because not every node
    # exists in every local graph
    for node in temporal_graph.get_nodes():
        if node.get_id() not in centrality_dict:
            centrality_dict[node.get_id()] = len(temporal_graph) * [0]
    # We also have to use an index because appending won't work with
    # nodes missing in some local graphs
    timestep = 0
    for local_graph in temporal_graph:
        # Skip empty graphs
        if not local_graph.get_edges():
            continue
        nx_graph = util.graph2networkx(local_graph)
        for (node_id, bc) in nx_centrality_func(nx_graph).items():
            centrality_dict[node_id][timestep] = bc
        timestep += 1
    return centrality_dict


class LocalDegreeCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)

        def nx_degree(nx_graph):
            return nx.degree_centrality(nx_graph)

        self._measures_dict = _networkx_local_centrality(graph, nx_degree)
        # Denormalize degrees
        for node_id in self._measures_dict:
            self._measures_dict[node_id] = list(map(lambda d: int(d * (len(graph.get_nodes()) - 1)), self._measures_dict[node_id]))

    @staticmethod
    def get_name() -> str:
        return "Local Degree Centrality"

    @staticmethod
    def get_description() -> str:
        return "Calculates node degree for every node"


class GlobalDegreeCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        nx_graph = util.temporal_graph2networkx(self._temporal_graph)
        self._measures_dict = nx.degree_centrality(nx_graph)
        # Denormalize degrees
        for node_id, degree in self._measures_dict.items():
            self._measures_dict[node_id] = int(degree * (len(graph.get_nodes()) - 1))

    @staticmethod
    def get_name() -> str:
        return "Global Degree Centrality"

    @staticmethod
    def get_description() -> str:
        return "Calculates degree for every node, which is the sum of all " \
               "local degrees"


class LocalBetweennessCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)

        def nx_betweenness(nx_graph):
            return nx.betweenness_centrality(nx_graph, normalized=True, weight=None)

        self._measures_dict = _networkx_local_centrality(graph, nx_betweenness)

    @staticmethod
    def get_name() -> str:
        return "Local Betweenness Centrality"

    @staticmethod
    def get_description() -> str:
        return "Calculates Betweenness Centrality of each node, defined by " \
               "amount of shortest paths in the local graph through this " \
               "node."


class GlobalBetweennessCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        nx_graph = util.temporal_graph2networkx(self._temporal_graph)
        self._measures_dict = nx.betweenness_centrality(nx_graph, normalized=True, weight=None)

    @staticmethod
    def get_name() -> str:
        return "Global Betweenness Centrality"

    @staticmethod
    def get_description() -> str:
        return "Calculates Betweenness Centrality of each node, defined by " \
               "amount of shortest paths in the global graph through this " \
               "node."


class LocalClosenessCentrality(LocalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)

        def nx_closeness(nx_graph):
            return nx.closeness_centrality(nx_graph, distance=None)

        self._measures_dict = _networkx_local_centrality(graph, nx_closeness)

    @staticmethod
    def get_name() -> str:
        return "Local Closeness Centrality"

    @staticmethod
    def get_description() -> str:
        return "Calculates Closeness Centrality of each node, defined by " \
               "the sum of the length of the shortest paths in the local " \
               "graph through this node."


class GlobalClosenessCentrality(GlobalNodeMeasure):
    def __init__(self, graph: vtna.graph.TemporalGraph):
        super().__init__(graph)
        nx_graph = util.temporal_graph2networkx(self._temporal_graph)
        self._measures_dict = nx.closeness_centrality(nx_graph, distance=None)

    @staticmethod
    def get_name() -> str:
        return "Global Closeness Centrality"

    @staticmethod
    def get_description() -> str:
        return "Calculates Closeness Centrality of each node, defined by " \
               "the sum of the length of the shortest paths in the global " \
               "graph through this node."
