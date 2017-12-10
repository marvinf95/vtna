__all__ = ['read_edge_table', 'group_edges_by_granularity', 'get_time_interval_of_edges', 'infer_update_delta',
           'MetadataTable', 'BadOrderError']

import typing as typ

import numpy as np
import pandas
import pandas.api.types

TemporalEdge = typ.Tuple[int, int, int]


def read_edge_table(graph_data_path: str, col_sep: str = None) -> typ.List[TemporalEdge]:
    """
    Loads edge table from given file path and returns as list of tuples (timestamp, node, node).

    Args:
        graph_data_path: Path to file of temporal graph data in the sociopatterns.org style.
            File can be raw-text or compressed with .gz/.bz2/.zip/.xz.
            File extension indicates the used compression.
            URL as path can be used, if no authentication is required to access resource.
        col_sep: Column separator. If not specified, any whitespace is recognized as separator.
    Raises:
        FileNotFoundError: Error occurs if the file path or URL is invalid.
    """
    if col_sep is None:
        col_sep = r'\s+'
    table = pandas.read_csv(graph_data_path,
                            sep=col_sep,  # Split at any whitespace. Files are either space or tab separated.
                            header=None,
                            names=['timestamp', 'node1', 'node2'],
                            usecols=[0, 1, 2],  # Ignore extra columns.
                            dtype={'timestamp': np.int32, 'node1': np.int32, 'node2': np.int32}
                            )
    return list(map(tuple, table.itertuples(index=False)))


def group_edges_by_granularity(edges: typ.List[TemporalEdge], granularity: int) -> typ.List[typ.List[TemporalEdge]]:
    """Groups edges into buckets of width granularity"""
    earliest, latest = get_time_interval_of_edges(edges)
    n_time_steps = int((latest - earliest) / granularity) + 1

    time_steps = [list() for _ in range(n_time_steps)]
    for edge in edges:
        timestamp = edge[0]
        time_step = (timestamp - earliest) // granularity
        time_steps[time_step].append(edge)
    return time_steps


def get_time_interval_of_edges(edges: typ.List[TemporalEdge]) -> typ.Tuple[int, int]:
    """Returns the earliest and latest timestamp of the given edges"""
    timestamps = list(map(lambda e: e[0], edges))
    return min(timestamps), max(timestamps)


def infer_update_delta(edges: typ.List[TemporalEdge]):
    """Returns update delta, which is the smallest time difference between two edge observations"""
    timestamps = sorted(set(map(lambda e: e[0], edges)))
    update_delta = min(timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1))
    return update_delta


class MetadataTable(object):
    def __init__(self, metadata_path: str, col_sep: str = None):
        if col_sep is None:
            col_sep = r'\s+'

        self.__table = pandas.read_csv(metadata_path,
                                       sep=col_sep,
                                       header=None,
                                       dtype={0: np.int32}
                                       )
        self.__table.rename({0: 'node'}, axis=1, inplace=True)
        self.__table.set_index('node', inplace=True)  # use node as index
        self.__table.rename(dict((col_idx, str(col_idx)) for col_idx in self.__table.columns), axis=1, inplace=True)
        # Force all columns to unordered categorical
        for col_name in self.__table.columns.values:
            self.__table[col_name] = self.__table[col_name].astype('category')

    def get_attribute_names(self) -> typ.Set[str]:
        return set(self.__table.columns.values).difference({'node'})

    def rename_attributes(self, names: typ.Dict[str, str]):
        self.__table.rename(names, axis=1, inplace=True)

    def get_categories(self, attribute: str) -> typ.List[str]:
        """Returns categories of specified attribute. If categories are not ordered, order will be arbitrary"""
        return list(self.__table[attribute].cat.categories)

    def is_ordered(self, attribute: str) -> bool:
        """Returns whether order has been applied on categories of specified attribute"""
        return self.__table[attribute].cat.ordered

    def order_categories(self, attribute: str, ordered_categories: typ.List[str]):
        """
        Applies order on categorical attribute. Existing ordering is overwritten.

        Args:
            attribute: Attribute to be ordered.
            ordered_categories: List of categories ordered from lowest to highest.
                List has to contain all categories exactly once.
        Raises:
            BadOrderError: Error is raised if provided ordered_categories does not match up with existing categories.
        """
        if set(ordered_categories) != set(self.__table[attribute].cat.categories) or \
                len(ordered_categories) != len(self.__table[attribute].cat.categories):
            raise BadOrderError(ordered_categories, self.__table[attribute].cat.categories, attribute)
        self.__table[attribute].cat.reorder_categories(ordered_categories, ordered=True, inplace=True)

    def remove_order(self, attribute: str):
        """Removes order from specified attribute"""
        self.__table[attribute].cat.reorder_categories(self.get_categories(attribute), ordered=False, inplace=True)

    def __getitem__(self, node: int) -> typ.Dict[str, str]:
        """
        Returns dictionary of attribute-value pairs of specified node.

        Args:
            node: Node as integer.
        Raises:
            KeyError: If specified node does not exist in metadata table.
            TypeError: If parameter node is not of type int.
        """
        if not isinstance(node, (int, np.integer)):
            raise TypeError(f'type {int} or {np.integer} expected, received type {type(node)}')
        return self.__table.loc[node].to_dict()

    def keys(self) -> typ.List[int]:
        return self.__table.index.values.tolist()

    def values(self) -> typ.List[typ.Dict[str, str]]:
        return [self[key] for key in self.keys()]

    def items(self) -> typ.List[typ.Tuple[int, typ.Dict[str, str]]]:
        return [(key, self[key]) for key in self.keys()]


class BadOrderError(Exception):
    def __init__(self, ordered_categories: typ.List[str], categories: typ.List[str], attribute: str):
        self.message = f'Provided order {ordered_categories} does not match up with categories {categories} ' \
                       f'of attribute {attribute}'
