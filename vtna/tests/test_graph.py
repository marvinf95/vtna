import unittest

import vtna.data_import as dimp
import vtna.graph as graph

class TestGraphCreation(unittest.TestCase):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
        graphs = graph.TemporalGraph(edges, meta, 20)

        def test_number_of_graphs(self):
            self.assertEqual(len(self.__class__.graphs), 12, 'created all graphs')

        def test_iterator_of_graphs(self):
            i = iter(self.__class__.graphs)
            next(i)
            self.assertEqual(len(next(i).get_edges()), 41, 'created all graphs') # i is the third graph in this case

        def test_get_edges(self):
            self.assertEqual(len(self.__class__.graphs[1].get_edges()), 37, 'Check number of edges')

        def test_get_edge(self):
            self.assertEqual(self.__class__.graphs[1].get_edge(122,255).get_count(), 1, 'Check number of edge')
            self.assertEqual(self.__class__.graphs[1].get_edge(122,255).get_timestamps(), [1385982040], 'Check timestamps of edge')
            self.assertEqual(self.__class__.graphs[1].get_edge(122,255).get_incident_nodes(), (122, 255), 'Check incident nodes of edge')

        def test_number_of_nodes(self):
            self.assertEqual(len(self.__class__.graphs.get_nodes()), 114, 'Correct node number')

        def test_get_node(self):
            self.assertEqual(self.__class__.graphs.get_node(871).get_id(), 871, 'Check node_id')

        def test_global_attributes(self):
            self.assertEqual(self.__class__.graphs.get_node(871).get_global_attribute('1'), '2BIO3', 'Check get_global_attribute')
            self.__class__.graphs.get_node(871).update_global_attribute('1','test')
            self.assertEqual(self.__class__.graphs.get_node(871).get_global_attribute('1'), 'test', 'Check get_global_attribute with overridden attribute')

        def test_local_attributes(self):
            self.__class__.graphs.get_node(871).update_local_attribute('1',['test1', 'test2', 4])
            self.assertEqual(self.__class__.graphs.get_node(871).get_local_attribute('1',0), 'test1', 'Check get_local_attribute with type string')
            self.assertEqual(self.__class__.graphs.get_node(871).get_local_attribute('1',2), 4, 'Check get_local_attribute with type int')

        def test_with_higher_granularity(self):
            graphs_high_granularity = graph.TemporalGraph(self.__class__.edges, self.__class__.meta, 60)
            self.assertEqual(len(graphs_high_granularity), 4, 'created all graphs')
            self.assertEqual(graphs_high_granularity[0].get_edge(122,255).get_count(), 3, 'Check number of edge') # Three occurences of 122 and 255 in the first three timestamps (60 seconds)
