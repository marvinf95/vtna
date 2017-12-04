import unittest

import vtna.node_measure as nome
import vtna.data_import as dimp
import vtna.graph as graph


class TestCentralityMeasures(unittest.TestCase):
    def setUp(self):
        edge_table = dimp.TemporalEdgeTable(
            'data/highschool_edges.ssv')
        self._temp_graph = graph.TemporalGraph(edge_table, None, 600)

    def test_local_degree_centrality(self):
        degree_centrality = nome.LocalDegreeCentrality(self._temp_graph)
        degree_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            dc = node.get_global_attribute(degree_centrality.get_name())
            print(node.get_id(), dc)

    def test_global_degree_centrality(self):
        degree_centrality = nome.GlobalDegreeCentrality(self._temp_graph)
        degree_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            dc = node.get_global_attribute(degree_centrality.get_name())
            print(node.get_id(), dc)

    def test_local_betweenness_centrality(self):
        betw_centrality = nome.LocalBetweennessCentrality(self._temp_graph)
        betw_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            bc = node.get_local_attribute(betw_centrality.get_name(), 1)
            print(node.get_id(), bc)

    def test_global_betweenness_centrality(self):
        betw_centrality = nome.GlobalBetweennessCentrality(self._temp_graph)
        betw_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            bc = node.get_local_attribute(betw_centrality.get_name(), 1)
            print(node.get_id(), bc)

    def test_local_closeness_centrality(self):
        clsns_centrality = nome.LocalClosenessCentrality(self._temp_graph)
        clsns_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            cc = node.get_local_attribute(clsns_centrality.get_name(), 1)
            print(node.get_id(), cc)

    def test_global_closeness_centrality(self):
        clsns_centrality = nome.GlobalClosenessCentrality(self._temp_graph)
        clsns_centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            cc = node.get_local_attribute(clsns_centrality.get_name(), 1)
            print(node.get_id(), cc)

