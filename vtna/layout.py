__all__ = ['flexible_spring_layout', 'static_spring_layout']

import typing as typ

import networkx as nx

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
def flexible_spring_layout(temp_graph: vtna.graph.TemporalGraph) -> typ.List[typ.Dict[int, Point]]:
    return [nx.spring_layout(util.graph2networkx(graph), dim=2, weight=None)
            for graph in temp_graph]


@is_static(True)
@name('Static Spring Layout')
@description('Basic Spring layout which ensures static node position by aggregating all observations')
def static_spring_layout(temp_graph: vtna.graph.TemporalGraph) -> typ.List[typ.Dict[int, Point]]:
    layout = nx.spring_layout(util.temporal_graph2networkx(temp_graph), dim=2, weight=None)
    return [layout.copy() for _ in range(len(temp_graph))]


@is_static(False)
@name('Flexible Weighted Spring Layout')
@description('Weighted Spring layout with one individual layout per time step. Nodes with high number of interactions '
             'are closer.')
def flexible_weighted_spring_layout(temp_graph: vtna.graph.TemporalGraph) -> typ.List[typ.Dict[int, Point]]:
    return [nx.spring_layout(util.graph2networkx(graph), dim=2, weight='count')
            for graph in temp_graph]


@is_static(True)
@name('Static Weighted Spring Layout')
@description('Weighted Spring layout which ensures static node position by aggregating all observations. Nodes with '
             'high number of interactions are closer.')
def static_weighted_spring_layout(temp_graph: vtna.graph.TemporalGraph) -> typ.List[typ.Dict[int, Point]]:
    layout = nx.spring_layout(util.temporal_graph2networkx(temp_graph), dim=2, weight='count')
    return [layout.copy() for _ in range(len(temp_graph))]