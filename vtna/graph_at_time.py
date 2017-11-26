__all__ = ['GraphAtTimestamp']


#import typing as typ
#import warnings

import pandas
import pandas.api.types
import numpy as np
import networkx as nx


class GraphAtTimestamp(object):
    def __init__(self, timestamp: int):
        """
        Creates graph at a specified timestamp.

        Args:
            timestamp: Timestamp at which the graph will be created.
        """
        # TODO: If no timestamps are given: Exception that no graph could be build
        self.__edges_at_timestamp = get_edges_at(timestamp)
        self.__graph_at_timestamp = nx.Graph().add_edges_from(timestamp)

        # TODO: Add attributes to nodes
        #for n in self.__graph_at_timestamp.nodes_iter():
        #    self.__attributes_at_timestamp = __getitem__(n)
        #    for k, v in n.items():
        #        nx.set_node_attributes(__graph_at_timestamp,)

            # TODO: Add attributes to nodes
