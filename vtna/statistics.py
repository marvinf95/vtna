import collections
import typing as typ

import vtna.graph


def total_edges_per_time_step(temp_graph: vtna.graph.TemporalGraph) -> typ.List[int]:
    return [sum(edge.get_count() for edge in graph.get_edges()) for graph in temp_graph]


def nodes_per_time_step(temp_graph: vtna.graph.TemporalGraph) -> typ.List[int]:
    return [len(set(node for edge in graph.get_edges() for node in edge.get_incident_nodes())) for graph in temp_graph]


def multi_step_interactions(temp_graph: vtna.graph.TemporalGraph, update_delta: int) \
        -> typ.Dict[typ.Tuple[int, int], typ.List[typ.Tuple[int, int]]]:
    """
    Args:
        temp_graph: vtna.graph.TemporalGraph.
        update_delta: int, smallest time distance between two observations.
    Returns:
        Dictionary, which maps edge to list of time intervals. Each time interval represents a continuous
           series of edges between two nodes. Intuitively, such a series of edges implies a ongoing conversation
           between nodes.
    """
    timestamps = collections.defaultdict(list)
    for graph in temp_graph:
        for edge in graph.get_edges():
            node1, node2 = sorted(edge.get_incident_nodes())
            timestamps[(node1, node2)].extend(edge.get_timestamps())
    interactions = dict()
    for edge in timestamps.keys():
        interactions[edge] = [(timestamps[edge][0], timestamps[edge][0])]
        for timestamp in timestamps[1:]:
            if interactions[edge][-1][1] == (timestamp - update_delta):
                interactions[edge][-1][1] = timestamp
            else:
                interactions[edge].append((timestamp, timestamp))
    return interactions


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


@name('Interactions per time')
@description('Number of interactions in a time interval')
def statistics_interactions(temp_graph: vtna.graph.TemporalGraph, time_step1: int, time_step2=None) -> int:
    """
            Retrieves a temporal graph and one or two time steps:
                One time step: The number of interactions of the given time step is returned.
                Two time steps: The number of interactions in the time interval of the two time steps is returned.

            Args:
                temp_graph: A temporal graph.
                time_step1: Either the time step for that the interactions are given back
                            or the start of the time interval.
                time_step2: Optional parameter: Defines the end of the time interval.
                
            Returns:
                 Integer of interactions at the timestep or the time interval.
                 
            Raises:
                IndexError: Is raised, if index int is not in the observation interval as specified by
                    get_earliest_timestamp() and get_latest_timestamp().
                TypeError: Is raised, if time_step2 is not an int.
            """
    interactions = 0
    if time_step2 is None:
        interactions = len(temp_graph[time_step1].get_edges())
    elif isinstance(time_step2, int):
        start = time_step1
        stop = time_step2
        while start <= stop:
            interactions += len(temp_graph[start].get_edges())
            start += 1
    else:
        raise TypeError(f'time_step2 must be of type int, not {type(time_step2)}')
    return interactions
