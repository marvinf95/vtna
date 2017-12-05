import warnings

__all__ = ['TemporalEdgeTable', 'MetadataTable', 'BadOrderError']


import typing as typ

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
        """Returns update delta, the minimal temporal distance between 2 observations."""
        return self.__update_delta

    def get_earliest_timestamp(self) -> int:
        """Returns the earliest timestamp, therefore defines the lower bound of the observation time interval."""
        return self.__min_timestamp

    def get_latest_timestamp(self) -> int:
        """Returns the latest timestamp, therefore defines the upper bound of the observation time interval."""
        return self.__max_timestamp

    def __getitem__(self, key: typ.Union[int, slice]) -> typ.Iterable[typ.Tuple[int, int, int]]:
        """
        Retrieves temporal edges based on single timestamp or time interval defined by slice.

        Args:
            key: Either an int or a slice. Slice can contain any combinations of int and None. Step is ignored in slice.
        Returns:
             An Iterable of tuples (timestamp, node1, node2), which are the temporal edges at the specified timestamp
             or in the specified time interval.
        Raises:
            IndexError: Is raised, if index int is not in the observation interval as specified by
                get_earliest_timestamp() and get_latest_timestamp().
            TypeError: Is raised, if key is not an int, or if start or stop (of slice) are not int or None.
        """
        if isinstance(key, (int, np.integer)):
            if not self.___is_in_time_interval(key):
                raise IndexError(f'index {key} out of range ({self.__min_timestamp},'f'{self.__max_timestamp})')
            df = self.__table[self.__table.timestamp == key][['timestamp', 'node1', 'node2']]
        elif isinstance(key, slice):
            start = key.start
            stop = key.stop
            # Step is not very useful to the given task and is therefore ignored
            if key.step is not None:
                warnings.warn(f'TemporalEdgeTable.__getitem__ ignores step attribute in slice', category=UserWarning)
            # Ensure both start and stop are either None or int
            if (start is not None and not isinstance(start, (int, np.integer))) or \
                    (stop is not None and not isinstance(stop, (int, np.integer))):
                raise TypeError('slice indices must be integers or None')
            # If start or stop are None set them to min or max respectively
            if start is None:
                start = self.__min_timestamp
            if stop is None:
                # max + 1 because retrieval is exclusive on stop, this ensures inclusion of max
                stop = self.__max_timestamp + 1
            df = self.__table[(self.__table.timestamp >= start) & (self.__table.timestamp < stop)][
                ['timestamp', 'node1', 'node2']]
        else:
            raise TypeError(f'indices must be integers or slices, not {type(key)}')
        return ((timestamp, node1, node2) for timestamp, node1, node2 in df.itertuples(index=False))

    def ___is_in_time_interval(self, timestamp: int) -> bool:
        return self.__min_timestamp <= timestamp <= self.__max_timestamp


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

