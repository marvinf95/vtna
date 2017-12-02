__all__ = ['FlexibleSpringLayout', 'StaticSpringLayout']

import abc
import copy
import typing as typ

import networkx as nx

import vtna.graph
import vtna.utility as util


Point = typ.Tuple[float, float]


class Layout(util.Describable, metaclass=abc.ABCMeta):
    def __init__(self, temp_graph: vtna.graph.TemporalGraph):
        self.__temp_graph = temp_graph
        self.__layout = None  # type: typ.List[typ.Dict[int, Point]]

    @abc.abstractmethod
    def compute(self):
        pass

    def __getitem__(self, time_step: typ.Union[slice, int]) -> typ.Dict[int, Point]:
        if self.__layout is None:
            raise NoComputedLayoutError()
        return copy.deepcopy(self.__layout[time_step])

    def __setitem__(self, time_step: int, mapping: typ.Dict[int, Point]):
        if self.__layout is None:
            raise NoComputedLayoutError()
        self.__layout[time_step].update(mapping)

    @abc.abstractmethod
    def is_static(self) -> bool:
        pass


class FlexibleLayout(Layout, metaclass=abc.ABCMeta):
    def compute(self):
        self.__layout = self.__compute_flexible_layout()

    def is_static(self) -> bool:
        return False

    @abc.abstractmethod
    def __compute_flexible_layout(self) -> typ.List[typ.Dict[int, Point]]:
        pass


class StaticLayout(Layout, metaclass=abc.ABCMeta):
    def compute(self):
        layout = self.__compute_static_layout()
        self.__layout = [layout.copy() for _ in range(len(self.__temp_graph))]

    def is_static(self) -> bool:
        return True

    @abc.abstractmethod
    def __compute_static_layout(self) -> typ.Dict[int, Point]:
        pass


class FlexibleSpringLayout(FlexibleLayout):
    def __init__(self, temp_graph: vtna.graph.TemporalGraph):
        super(FlexibleSpringLayout, self).__init__(temp_graph)

    def __compute_flexible_layout(self) -> typ.List[typ.Dict[int, Point]]:
        return [nx.spring_layout(util.graph2networkx(util.graph2networkx(graph)), dim=2, weight=None)
                for graph in self.__temp_graph]

    def get_name(self) -> str:
        return 'Flexible Spring Layout'

    def get_description(self) -> str:
        return 'Basic Spring layout with one individual layout per timestep'


class StaticSpringLayout(StaticLayout):
    def __init__(self, temp_graph: vtna.graph.TemporalGraph):
        super(StaticSpringLayout, self).__init__(temp_graph)

    def __compute_static_layout(self):
        return nx.spring_layout(util.temporal_graph2networkx(self.__temp_graph), dim=2, weight=None)

    def get_name(self) -> str:
        return 'Static Spring Layout'

    def get_description(self) -> str:
        return 'Basic Spring layout which ensures static node position by aggregating all observations'


class NoComputedLayoutError(Exception):
    def __init__(self):
        self.message = 'No layout exists. Call compute() to create the layout.'
