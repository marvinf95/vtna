__all__ = ['TemporalEdgeTable']


import typing as typ

import pandas
import numpy as np


class TemporalEdgeTable(object):

    def __init__(self, graph_data_path: str):
        """
        Loads table of edges indexed by timestamp from given path.

        Args:
            graph_data_path: Path to file of temporal graph data in the sociopatterns.org style.
                File can be raw-text or compressed with .gz, .bz2, .zip, .xz. Extension has to indicate
                the used compression.
                URL as path can be used, if no authentication is required to access resource.
                File has no headers. Rows are whitespace-separated (e.g. space, tab).
                Only first 3 columns are read and have the content: timestamp node node
                timestamp and node are both integers.
        Raises:
            FileNotFoundError: Error occurs if the file path or URL is invalid.

        """
        self.__table = pandas.read_csv(graph_data_path,
                                       sep='\s+',  # Split at any whitespace. Files are either space or tab separated.
                                       header=None,
                                       names=['timestamp', 'node1', 'node2'],
                                       usecols=[0, 1, 2],  # Ignore extra columns.
                                       dtype={'timestamp': np.int32, 'node1': np.int32, 'node2': np.int32}
                                       )
        timestamps = set(self.__table['timestamp'])
        self.__update_delta = min(abs(t1 - t2) for t1 in timestamps for t2 in timestamps if t1 != t2)

    def get_edges_at(self, timestamp: int) -> typ.List[typ.Tuple[int, int]]:
        timestamp_df = self.__table[self.__table.timestamp == timestamp][['node1', 'node2']]
        return [(node1, node2) for node1, node2 in timestamp_df.itertuples(index=False)]

    def get_update_delta(self) -> int:
        return self.__update_delta

    def get_earliest_timestamp(self) -> int:
        return self.__table['timestamp'].min()

    def get_latest_timestamp(self) -> int:
        return self.__table['timestamp'].max()
