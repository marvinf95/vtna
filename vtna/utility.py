import abc
import collections as col

import networkx

import vtna.graph


class Describable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass


def graph2networkx(graph: vtna.graph.Graph) -> networkx.Graph:
    nx_graph = networkx.Graph()
    nx_graph.add_edges_from(edge.get_incident_nodes() + ({'count': edge.get_count()},) for edge in graph.get_edges())
    return nx_graph


def temporal_graph2networkx(temp_graph: vtna.graph.TemporalGraph) -> networkx.Graph:
    edges = col.defaultdict(int)
    for graph in temp_graph:
        for edge in graph.get_edges():
            edges[tuple(sorted(edge.get_incident_nodes()))] += edge.get_count()
    nx_graph = networkx.Graph()
    nx_graph.add_edges_from(edge + ({'count': count},) for edge, count in edges.items())
    return nx_graph
