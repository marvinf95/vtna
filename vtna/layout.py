__all__ = []  # export actual implementations of classes

import abc
import typing as typ

import vtna.graph


Point = typ.Tuple[float, float]
PointOrPoints = typ.Union[Point, typ.List[Point]]
TimeStepArg = typ.Union[int, slice]


class Layout(abc.ABC):
    def __init__(self, temp_graph: vtna.graph.TemporalGraph):
        self.__temp_graph = temp_graph

    @abc.abstractmethod
    def compute(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, time_step: TimeStepArg) -> typ.Dict[int, Point]:
        pass

    @abc.abstractmethod
    def __setitem__(self, time_step: TimeStepArg, mapping: typ.Dict[int, PointOrPoints]):
        pass

    @abc.abstractmethod
    def is_static(self) -> bool:
        pass

# We should probably create a StaticLayout and FlexibleLayout subclass,
# because of similar/identical getitem, setitem behaviour for each type.
