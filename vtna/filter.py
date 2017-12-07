import typing as typ

import vtna.graph

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


@name('Filter Attributes')
@description('Filter for special values in attributes')
def filter_attributes(temp_graph: vtna.graph.TemporalGraph, name: str, value: vtna.graph.AttributeValue) -> typ.List[int]:
    filter_list = []
    for i in temp_graph.get_nodes():
        if i.get_global_attribute(name) == value:
            filter_list.append(i.get_id())
    return filter_list
