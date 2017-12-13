import collections
import typing as typ

import numpy as np

import vtna.graph


Edge = typ.Tuple[int, int]
TimeInterval = typ.Tuple[int, int]


def total_edges_per_time_step(graphs: typ.Iterable[vtna.graph.Graph]) -> typ.List[int]:
    return [sum(edge.get_count() for edge in graph.get_edges()) for graph in graphs]


def nodes_per_time_step(graphs: typ.Iterable[vtna.graph.Graph]) -> typ.List[int]:
    return [len(set(node for edge in graph.get_edges() for node in edge.get_incident_nodes())) for graph in graphs]


def multi_step_interactions(graphs: typ.Iterable[vtna.graph.Graph], update_delta: int) \
        -> typ.Dict[Edge, typ.List[TimeInterval]]:
    """
    Args:
        graphs: Iterable of vtna.graph.Graph objects
        update_delta: int, smallest time distance between two observations.
    Returns:
        Dictionary, which maps edge to list of time intervals. Each time interval represents a continuous
           series of edges between two nodes. Intuitively, such a series of edges implies a ongoing conversation
           between nodes.
    """
    timestamps = collections.defaultdict(list)
    for graph in graphs:
        for edge in graph.get_edges():
            node1, node2 = sorted(edge.get_incident_nodes())
            timestamps[(node1, node2)].extend(edge.get_timestamps())
    interactions = dict()
    for edge in timestamps.keys():
        interactions[edge] = [(timestamps[edge][0], timestamps[edge][0])]
        for timestamp in timestamps[edge][1:]:
            if interactions[edge][-1][1] == (timestamp - update_delta):
                interactions[edge][-1] = (interactions[edge][-1][0], timestamp)
            else:
                interactions[edge].append((timestamp, timestamp))
    return interactions


def mean_stdev_numeric_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str) \
        -> typ.Tuple[float, float]:
    values = [node.get_global_attribute(attribute_name) for node in nodes]
    return float(np.mean(values)), float(np.std(values))


def median_ordinal_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str,
                             order: typ.List[str]) -> str:
    cat2idx = dict((cat, idx) for idx, cat in enumerate(order))
    median = np.median([cat2idx[node.get_global_attribute(attribute_name)] for node in nodes])
    return order[int(median)]


def mode_categorical_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str) -> str:
    values = [node.get_global_attribute(attribute_name) for node in nodes]
    return max(set(values), key=values.count)


def histogram_categorical_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str) \
        -> typ.Dict[str, int]:
    hist = collections.Counter()
    hist.update(node.get_global_attribute(attribute_name) for node in nodes)
    return hist
