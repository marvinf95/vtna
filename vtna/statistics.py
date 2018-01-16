import collections
import typing as typ

import numpy as np

import vtna.data_import
import vtna.graph


Edge = typ.Tuple[int, int]
TimeInterval = typ.Tuple[int, int]

"""
A static helper module that is used for computing basic statistics about
our graphs.
"""


def total_edges_per_time_step(graphs: typ.Iterable[vtna.graph.Graph]) -> typ.List[int]:
    """
    Returns the amount of singular edges as a list over all timesteps.
    Note that an edge of a local graph usually represents multiple, aggregated
    edges/interactions.
    """
    return [sum(edge.get_count() for edge in graph.get_edges()) for graph in graphs]


def histogram_edges(edges: typ.List[typ.Tuple[int, int, int]], granularity: int=None) -> typ.List[int]:
    """
    Returns the amount of singular edges as a list over timesteps defined through
    the provided granularity parameter.

    Args:
        edges: A list of edge tuples, consisting of (timestamp, node1, node2)
        granularity: The length of a timestep. If None, the smallest update
            delta will be inferred and used.
    """
    if len(edges) == 0:
        return list()
    if granularity is None:
        granularity = vtna.data_import.infer_update_delta(edges)
    histogram = [len(ls) for ls in vtna.data_import.group_edges_by_granularity(edges, granularity)]
    return histogram


def nodes_per_time_step(graphs: typ.Iterable[vtna.graph.Graph]) -> typ.List[int]:
    """Returns amount of nodes per timestep in a list over all timesteps."""
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
    """
    Retrieves numeric global attribute values with name attribute_name of the
    provided nodes and returns mean and standard deviation of the attribute
    values as a tuple.
    """
    values = [node.get_global_attribute(attribute_name) for node in nodes]
    return float(np.mean(values)), float(np.std(values))


def median_ordinal_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str,
                             order: typ.List[str]) -> str:
    """
    Returns the median attribute value of an ordinal, global attribute.

    Args:
        nodes: The nodes which attribute values will be retrieved and compared
        attribute_name: The name of the ordinal attribute
        order: A list that defines the order of the attribute values
    """
    cat2idx = dict((cat, idx) for idx, cat in enumerate(order))
    median = np.median([cat2idx[node.get_global_attribute(attribute_name)] for node in nodes])
    return order[int(median)]


def mode_categorical_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str) -> str:
    """Returns the global, categorical attribute value that occurs most often."""
    values = [node.get_global_attribute(attribute_name) for node in nodes]
    return max(set(values), key=values.count)


def histogram_categorical_attribute(nodes: typ.Iterable[vtna.graph.TemporalNode], attribute_name: str) \
        -> typ.Dict[str, int]:
    """
    Returns a dictionary that contains attribute values of a global attribute
    as keys and their occurence count as values.

    Args:
        nodes: The nodes which attribute values will be considered
        attribute_name: The name of the global categorical attribute
    """
    hist = collections.Counter()
    hist.update(node.get_global_attribute(attribute_name) for node in nodes)
    return hist
