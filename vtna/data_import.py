__all__ = ['TemporalEdgeTable']


import typing as typ
import warnings

import pandas
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
            col_sep = '\s+'
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

    def get_edges_at(self, timestamp: int) -> typ.List[typ.Tuple[int, int]]:
        if type(timestamp) != int:
            raise TypeError(f'type {int} expected, received type {type(timestamp)}')
        if not(self.__min_timestamp <= timestamp <= self.__max_timestamp):
            raise IndexError(f'timestamp {timestamp} out of range ({self.__min_timestamp}, {self.__max_timestamp})')
        if timestamp % self.__update_delta != 0:
            msg = f'queried timestamp {timestamp} is not a multiple of delta {self.__update_delta}'
            warnings.warn(msg)
        timestamp_df = self.__table[self.__table.timestamp == timestamp][['node1', 'node2']]
        return [(node1, node2) for node1, node2 in timestamp_df.itertuples(index=False)]

    def __getitem__(self, item) -> typ.List[typ.Tuple[int, int]]:
        return self.get_edges_at(item)

    def get_update_delta(self) -> int:
        return self.__update_delta

    def get_earliest_timestamp(self) -> int:
        return self.__min_timestamp

    def get_latest_timestamp(self) -> int:
        return self.__max_timestamp
