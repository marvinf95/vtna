__all__ = ['TemporalGraph', 'Graph', 'TemporalNode', 'Edge']

import typing as typ

import vtna.data_import as dimp

# Type Alias
AttributeValue = typ.Union[str, float]


class TemporalGraph(object):
    def __init__(self, edge_table: dimp.TemporalEdgeTable, meta_table: dimp.MetadataTable, granularity: int):
        pass

    def __getitem__(self, time_step: int) -> 'Graph':
        pass

    def __len__(self):
        pass

    def get_nodes(self) -> typ.List['TemporalNode']:
        pass

    def get_node(self, node_id: int) -> 'TemporalNode':
        pass


class Graph(object):
    def __init__(self, edges: typ.List['Edge']):
        pass

    def get_edges(self) -> typ.List['Edge']:
        pass

    def get_edge(self, node1: int, node2: int) -> 'Edge':
        pass


class TemporalNode(object):
    def __init__(self, node_id: int, meta_attributes: typ.Dict[str, str]):
        pass

    def get_id(self) -> int:
        pass

    def get_global_attribute(self, name: str) -> AttributeValue:
        pass

    def get_local_attribute(self, name: str, time_step: int) -> AttributeValue:
        pass

    def update_global_attribute(self, name: str, value: AttributeValue):
        pass

    def update_local_attribute(self, name: str, values: typ.List[AttributeError]):
        pass


class Edge(object):
    def __init__(self, node1: int, node2: int, time_stamps: typ.List[int]):
        pass

    def get_incident_nodes(self) -> typ.Tuple[int, int]:
        pass

    def get_count(self) -> int:
        pass

    def get_timestamps(self) -> typ.List[int]:
        pass

    # We may add edge measures in the future.
