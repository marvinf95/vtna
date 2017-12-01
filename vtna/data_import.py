__all__ = ['TemporalEdgeTable', 'MetadataTable', 'BadOrderError']


import typing as typ
import warnings

import pandas
import pandas.api.types
import numpy as np


class TemporalEdgeTable(object):
    def __init__(self, graph_data_path: str, col_sep: str=None):
        """
        Loads table of edges indexed by timestamp from given path.

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
        self.__table = pandas.read_csv(graph_data_path,
                                       sep=col_sep,  # Split at any whitespace. Files are either space or tab separated.
                                       header=None,
                                       names=['timestamp', 'node1', 'node2'],
                                       usecols=[0, 1, 2],  # Ignore extra columns.
                                       dtype={'timestamp': np.int32, 'node1': np.int32, 'node2': np.int32}
                                       )
        timestamps = set(self.__table['timestamp'])
        self.__update_delta = min(abs(t1 - t2) for t1 in timestamps for t2 in timestamps if t1 != t2)
        self.__min_timestamp = self.__table['timestamp'].min()
        self.__max_timestamp = self.__table['timestamp'].max()

    def get_update_delta(self) -> int:
        return self.__update_delta

    def get_earliest_timestamp(self) -> int:
        return self.__min_timestamp

    def get_latest_timestamp(self) -> int:
        return self.__max_timestamp

    def __getitem__(self, timestamp) -> typ.List[typ.Tuple[int, int]]:
        if type(timestamp) != int:
            raise TypeError(f'type {int} expected, received type {type(timestamp)}')
        if not(self.__min_timestamp <= timestamp <= self.__max_timestamp):
            raise IndexError(f'timestamp {timestamp} out of range ({self.__min_timestamp}, {self.__max_timestamp})')
        if timestamp % self.__update_delta != 0:
            msg = f'queried timestamp {timestamp} is not a multiple of delta {self.__update_delta}'
            warnings.warn(msg)
        timestamp_df = self.__table[self.__table.timestamp == timestamp][['node1', 'node2']]
        return [(node1, node2) for node1, node2 in timestamp_df.itertuples(index=False)]


class MetadataTable(object):
    def __init__(self, metadata_path: str, col_sep: str=None):
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
        if set(ordered_categories) != set(self.__table[attribute].cat.categories) and \
           len(ordered_categories) == len(self.__table.cat.categories):
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
        if type(node) != int:
            raise TypeError(f'type {int} expected, received type {type(node)}')
        return self.__table.ix[node].to_dict()

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

