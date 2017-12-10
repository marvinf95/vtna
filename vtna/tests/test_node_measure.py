import unittest

from nose.tools import raises

import vtna.data_import as dimp
import vtna.graph as graph
import vtna.node_measure as nome


class TestCentralityMeasures(unittest.TestCase):
    def setUp(self):
        edges = dimp.read_edge_table('vtna/tests/data/highschool_edges.ssv')
        self._temp_graph = graph.TemporalGraph(edges, None, 20)

    def test_local_degree_centrality(self):
        degree_centrality = nome.LocalDegreeCentrality(self._temp_graph)
        self.assertIsNotNone(degree_centrality.get_description())
        degree_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            _ = node.get_local_attribute(degree_centrality.get_name(), 1)

    def test_global_degree_centrality(self):
        degree_centrality = nome.GlobalDegreeCentrality(self._temp_graph)
        self.assertIsNotNone(degree_centrality.get_description())
        degree_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            _ = node.get_global_attribute(degree_centrality.get_name())

    def test_local_betweenness_centrality(self):
        betw_centrality = nome.LocalBetweennessCentrality(self._temp_graph)
        self.assertIsNotNone(betw_centrality.get_description())
        betw_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            _ = node.get_local_attribute(betw_centrality.get_name(), 1)

    def test_global_betweenness_centrality(self):
        betw_centrality = nome.GlobalBetweennessCentrality(self._temp_graph)
        self.assertIsNotNone(betw_centrality.get_description())
        betw_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            _ = node.get_global_attribute(betw_centrality.get_name())

    def test_local_closeness_centrality(self):
        clsns_centrality = nome.LocalClosenessCentrality(self._temp_graph)
        self.assertIsNotNone(clsns_centrality.get_description())
        clsns_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            _ = node.get_local_attribute(clsns_centrality.get_name(), 1)

    def test_global_closeness_centrality(self):
        clsns_centrality = nome.GlobalClosenessCentrality(self._temp_graph)
        self.assertIsNotNone(clsns_centrality.get_description())
        clsns_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            _ = node.get_global_attribute(clsns_centrality.get_name())

    @raises(TypeError)
    def test_lbc_getitem_invalid_parameter(self):
        nome.LocalDegreeCentrality(self._temp_graph).__getitem__("NotAnInteger")

    @raises(TypeError)
    def test_gcc_getitem_invalid_parameter(self):
        nome.GlobalClosenessCentrality(self._temp_graph).__getitem__("NotAnInteger")

    @raises(TypeError)
    def test_lbc_init_invalid_parameter(self):
        nome.LocalDegreeCentrality(self._temp_graph).__init__("NotATemporalGraph")