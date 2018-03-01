import abc
import collections as col

import networkx

import vtna.graph

"""
Contains mutliple helper methods that are used in various modules.
"""


class Describable(metaclass=abc.ABCMeta):
    """
    A base class for objects that can be described.
    Contains abstract methods that are used as decorators, which tell e.g.
    the frontend / the user technical information.
    """
    @staticmethod
    @abc.abstractmethod
    def get_name() -> str:
        """A user friendly and descriptive name"""
        pass

    @staticmethod
    @abc.abstractmethod
    def get_description() -> str:
        """Short summary of idea and applications"""
        pass


def graph2networkx(graph: vtna.graph.Graph) -> networkx.Graph:
    """
    Converts a vtna graph to a networkx graph.
    Also adds a 'count' attribute to edges, which describes the amount this
    interaction happened in the local graph (which contains aggregated timesteps).

    Args:
         graph: A vtna local graph object
    """
    nx_graph = networkx.Graph()
    nx_graph.add_edges_from(tuple(sorted(edge.get_incident_nodes())) + ({'count': edge.get_count()},)
                            for edge in graph.get_edges())
    return nx_graph


def temporal_graph2networkx(temp_graph: vtna.graph.TemporalGraph) -> networkx.Graph:
    """
    Aggregates all edges in the provided temporal graph to create a static/global
    graph over all existing timesteps, as a networkx graph.
    Also adds a 'count' attribute to edges, which describes the amount this
    interaction happend over all timesteps (total interactions).
    Nodes with no edges are NOT added.

    Args:
        A vtna temporal graph object
    """
    edges = col.defaultdict(int)
    for graph in temp_graph:
        for edge in graph.get_edges():
            edges[tuple(sorted(edge.get_incident_nodes()))] += edge.get_count()
    nx_graph = networkx.Graph()
    nx_graph.add_edges_from(edge + ({'count': count},) for edge, count in edges.items())
    return nx_graph
