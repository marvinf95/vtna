"""
Module vtna.layout

The layout module contains a set of functions for the computation of layouts for temporal graphs.
Each function has the following attributes:
* is_static : bool, which signals whether the chosen function will provide the same layout for each time step or if
    each time step has an individually computed layout.
* name : str, human-readable name of the layout algorithm.
* description : str, short textual description of the layout algorithm.

In general, flexible layout function will take a longer computation as multiple separate layouts have to be computed.
However, flexible layouts usually produce easier to view layouts.
Static layouts are completely stable in regards to node positions unlike flexible layouts.

All spring-based layouts have the following adjustable hyperparameters:
* node_distance_scale: int, default: 1.0, constant scaling factor which influences the "pushing" factor of nodes.
    Higher values will create higher distances between connected nodes.
* n_iterations: int, default: 50, number of iterations the spring layout will take to compute the layout.
    More iterations may improve the quality of the layout, reducing the number of iterations will linearly decrease
    runtime.
"""
__all__ = ['flexible_spring_layout', 'static_spring_layout', 'flexible_weighted_spring_layout',
           'static_weighted_spring_layout']

import typing as typ

import networkx as nx
import numpy as np

import vtna.graph
import vtna.utility as util


Point = typ.Tuple[float, float]


def is_static(static: bool):
    """Decorator, adds is_static attribute to layout function."""
    def decorator(func):
        func.is_static = static
        return func
    return decorator


def name(n: str):
    """Decorator, adds name attribute to layout function."""
    def decorator(func):
        func.name = n
        return func
    return decorator


def description(d: str):
    """Decorator, adds description attribute to layout function."""
    def decorator(func):
        func.description = d
        return func
    return decorator


@is_static(False)
@name('Flexible Spring Layout')
@description('Basic Spring layout with one individual layout per time step')
def flexible_spring_layout(temp_graph: vtna.graph.TemporalGraph,
                           node_distance_scale: float=1.0,
                           n_iterations: int=50) -> typ.List[typ.Dict[int, Point]]:
    graphs = [util.graph2networkx(graph) for graph in temp_graph]
    node_distances = [node_distance_scale * __default_node_distance(graph) for graph in graphs]
    return [nx.spring_layout(graphs[i], dim=2, weight=None, iterations=n_iterations, k=node_distances[i])
            for i in range(len(graphs))]


@is_static(True)
@name('Static Spring Layout')
@description('Basic Spring layout which ensures static node position by aggregating all observations')
def static_spring_layout(temp_graph: vtna.graph.TemporalGraph,
                         node_distance_scale: float=1.0,
                         n_iterations: int=50) -> typ.List[typ.Dict[int, Point]]:
    graph = util.temporal_graph2networkx(temp_graph)
    node_distance = node_distance_scale * __default_node_distance(graph)
    layout = nx.spring_layout(graph, dim=2, weight=None, k=node_distance, iterations=n_iterations)
    return [layout.copy() for _ in range(len(temp_graph))]


@is_static(False)
@name('Flexible Weighted Spring Layout')
@description('Weighted Spring layout with one individual layout per time step. Nodes with high number of interactions '
             'are closer.')
def flexible_weighted_spring_layout(temp_graph: vtna.graph.TemporalGraph,
                                    node_distance_scale: float=1.0,
                                    n_iterations: int=50) -> typ.List[typ.Dict[int, Point]]:
    graphs = [util.graph2networkx(graph) for graph in temp_graph]
    node_distances = [node_distance_scale * __default_node_distance(graph) for graph in graphs]
    return [nx.spring_layout(graphs[i], dim=2, weight='count', iterations=n_iterations, k=node_distances[i])
            for i in range(len(graphs))]


@is_static(True)
@name('Static Weighted Spring Layout')
@description('Weighted Spring layout which ensures static node position by aggregating all observations. Nodes with '
             'high number of interactions are closer.')
def static_weighted_spring_layout(temp_graph: vtna.graph.TemporalGraph,
                                  node_distance_scale: float=1.0,
                                  n_iterations: int=50) -> typ.List[typ.Dict[int, Point]]:
    graph = util.temporal_graph2networkx(temp_graph)
    node_distance = node_distance_scale * __default_node_distance(graph)
    layout = nx.spring_layout(graph, dim=2, weight='count', k=node_distance, iterations=n_iterations)
    return [layout.copy() for _ in range(len(temp_graph))]


def __default_node_distance(graph: nx.Graph) -> float:
    return 1.0/np.sqrt(len(graph.nodes()))