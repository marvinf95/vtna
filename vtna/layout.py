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
import scipy as sp
import scipy.spatial
import sklearn.decomposition as decomposition
import sklearn.preprocessing as preprocessing

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
    layouts = list()
    for graph in map(util.graph2networkx, temp_graph):
        if len(graph.nodes()) == 0:
            layout = dict()
        else:
            node_distance = node_distance_scale * __default_node_distance(graph)
            layout = nx.spring_layout(graph, dim=2, weight=None, iterations=n_iterations, k=node_distance)
        layouts.append(layout)
    return layouts


@is_static(True)
@name('Static Spring Layout')
@description('Basic Spring layout which ensures static node position by aggregating all observations')
def static_spring_layout(temp_graph: vtna.graph.TemporalGraph,
                         node_distance_scale: float=1.0,
                         n_iterations: int=50) -> typ.List[typ.Dict[int, Point]]:
    graph = util.temporal_graph2networkx(temp_graph)
    if (len(graph.nodes())) == 0:
        layout = dict()
    else:
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
    layouts = list()
    for graph in map(util.graph2networkx, temp_graph):
        if len(graph.nodes()) == 0:
            layout = dict()
        else:
            node_distance = node_distance_scale * __default_node_distance(graph)
            layout = nx.spring_layout(graph, dim=2, weight='count', iterations=n_iterations, k=node_distance)
        layouts.append(layout)
    return layouts


@is_static(True)
@name('Static Weighted Spring Layout')
@description('Weighted Spring layout which ensures static node position by aggregating all observations. Nodes with '
             'high number of interactions are closer.')
def static_weighted_spring_layout(temp_graph: vtna.graph.TemporalGraph,
                                  node_distance_scale: float=1.0,
                                  n_iterations: int=50) -> typ.List[typ.Dict[int, Point]]:
    graph = util.temporal_graph2networkx(temp_graph)
    if (len(graph.nodes())) == 0:
        layout = dict()
    else:
        node_distance = node_distance_scale * __default_node_distance(graph)
        layout = nx.spring_layout(graph, dim=2, weight='count', k=node_distance, iterations=n_iterations)
    return [layout.copy() for _ in range(len(temp_graph))]


@is_static(True)
@name('Random Walk PCA Layout with Repel')
@description('Random Walk PCA uses the similarity of random walks from each node in the graph to build a '
             '2d representation of nodes via PCA. With an iterative repel mechanism overlapping nodes are separated.')
def random_walk_pca_layout(temp_graph: vtna.graph.TemporalGraph, n: int=25, repel: float=1.0, p: int=2,
                           random_state: int=None) -> typ.List[typ.Dict[int, Point]]:
    # TODO: Documentation
    # TODO: Optimize via vectorization
    # Mappings: node ID -> index, index -> node ID
    idx2node = [node.get_id() for node in temp_graph.get_nodes()]
    node2idx = dict((node_id, idx) for idx, node_id in enumerate(idx2node))
    # Build adjacency matrix
    nxgraph = util.temporal_graph2networkx(temp_graph)
    n_nodes = len(nxgraph.nodes())
    adjacency_matrix = np.zeros(shape=(n_nodes, n_nodes), dtype=np.float)
    for n1, n2, data in nxgraph.edges(data=True):
        adjacency_matrix[node2idx[n1], node2idx[n2]] = data['count']
        adjacency_matrix[node2idx[n2], node2idx[n1]] = data['count']
    # Compute random walk probabilities
    adj_prob =  adjacency_matrix / np.sum(adjacency_matrix, axis=0)
    walks = np.linalg.matrix_power(adj_prob, n).T
    # Compute distances between random walks of each node
    walk_dist = np.zeros(shape=adjacency_matrix.shape, dtype=np.float)
    for row in range(walk_dist.shape[0]):
        for col in range(walk_dist.shape[1]):
            walk_dist[row, col] = sp.spatial.distance.minkowski(walks[row], walks[col], p=p)
    # Compute PCA on random walk distances
    walks_dist_x = preprocessing.scale(walk_dist)
    pca = decomposition.PCA(n_components=2, random_state=random_state)
    walks_dist_2d = pca.fit_transform(walks_dist_x)
    # Apply repel on each node iteratively
    for n1 in range(walks_dist_2d.shape[0]):
        for n2 in range(walks_dist_2d.shape[0]):
            if n1 == n2:
                continue
            dist = sp.spatial.distance.minkowski(walks_dist_2d[n1], walks_dist_2d[n2], p=p)
            walks_dist_2d[n2] = walks_dist_2d[n2] + (repel/dist) * (walks_dist_2d[n2] - walks_dist_2d[n1])
    # Build layout dict from layout matrix
    layout = dict()
    for i in range(walks_dist_2d.shape[0]):
        layout[idx2node[i]] = (walks_dist_2d[i, 0], walks_dist_2d[i, 1])
    layouts = [layout.copy() for _ in range(len(temp_graph))]
    return layouts


def __default_node_distance(graph: nx.Graph) -> float:
    return 1.0/np.sqrt(len(graph.nodes()))
