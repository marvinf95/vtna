import typing as typ

import vtna.graph as graph


class NodeFilter(object):
    def __init__(self, predicate: typ.Callable[[graph.TemporalNode], bool]):
        self.predicate = predicate

    def __add__(self, other: 'NodeFilter') -> 'NodeFilter':
        """UNION of two NodeFilter objects"""
        if not isinstance(other, NodeFilter):
            raise TypeError(f'expected type {NodeFilter}, received type {type(other)}')
        new_filter = NodeFilter(lambda n: self.predicate(n) or other.predicate(n))
        return new_filter

    def __mul__(self, other: 'NodeFilter') -> 'NodeFilter':
        """INTERSECTION of two NodeFilter objects"""
        if not isinstance(other, NodeFilter):
            raise TypeError(f'expected type {NodeFilter}, received type {type(other)}')
        new_filter = NodeFilter(lambda n: self.predicate(n) and other.predicate(n))
        return new_filter

    def __sub__(self, other: 'NodeFilter') -> 'NodeFilter':
        """DIFFERENCE of two NodeFilter objects"""
        if not isinstance(other, NodeFilter):
            raise TypeError(f'expected type {NodeFilter}, received type {type(other)}')
        new_filter = NodeFilter(lambda n: self.predicate(n) and not other.predicate(n))
        return new_filter

    def __neg__(self) -> 'NodeFilter':
        """COMPLEMENT of two NodeFilter objects"""
        new_filter = NodeFilter(lambda n: not self.predicate(n))
        return new_filter

    def __call__(self, nodes: typ.Iterable[graph.TemporalNode]) -> typ.Iterable[graph.TemporalNode]:
        """Call NodeFilter object to apply filter to iterable of TemporalNode objects"""
        def __gen():
            for node in nodes:
                if self.predicate(node):
                    yield node
        return __gen()


def categorical_attribute_equal(attribute_name: str, attribute_value: str) -> typ.Callable[[graph.TemporalNode], bool]:
    def __pred(n: graph.TemporalNode) -> bool:
        return n.get_global_attribute(attribute_name) == attribute_value
    return __pred


def ordinal_attribute_greater_than_equal(attribute_name: str, lower_bound: str, order: typ.List[str]) \
        -> typ.Callable[[graph.TemporalNode], bool]:
    att2int = dict((val, idx) for idx, val in enumerate(order))

    def __pred(n: graph.TemporalNode) -> bool:
        val = n.get_global_attribute(attribute_name)
        return att2int[lower_bound] <= att2int[val]
    return __pred


def ordinal_attribute_greater_than(attribute_name: str, lower_bound: str, order: typ.List[str]):
    att2int = dict((val, idx) for idx, val in enumerate(order))

    def __pred(n: graph.TemporalNode) -> bool:
        val = n.get_global_attribute(attribute_name)
        return att2int[lower_bound] < att2int[val]
    return __pred
