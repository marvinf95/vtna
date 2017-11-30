import abc
import typing as typ

import vtna.graph


class NodeMeasure(abc.ABC):
    @abc.abstractmethod
    def __init__(self, graph: vtna.graph.TemporalGraph):
        pass

    @abc.abstractmethod
    def add_to_graph(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, node_id: int):
        pass

# Other than computation, most functionality can be implemented in the abstract classes LocalNodeMeasure
# and GlobalNodeMeasure


class LocalNodeMeasure(NodeMeasure, abc.ABC):
    @abc.abstractmethod
    def __getitem__(self, node_id: int) -> typ.Dict[int, float]:
        pass


class GlobalNodeMeasure(NodeMeasure, abc.ABC):
    @abc.abstractmethod
    def __getitem__(self, node_id: int) -> float:
        pass
