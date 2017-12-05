import unittest

import vtna.data_import as dimp
import vtna.graph as graph

class TestGraphCreation(unittest.TestCase):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
        graphs = graph.TemporalGraph(edges, meta, 20)

        def test_number_of_graphs(self):
            self.assertEqual(len(self.__class__.graphs), 12, 'created all graphs')

        def test_number_of_nodes(self):
            self.assertEqual(len(self.__class__.graphs.get_nodes()), 114, 'Correct node number')

        def test_node(self):
            self.assertEqual(self.__class__.graphs.get_node(871).get_id(), (871), 'Check node_id')
            #self.assertEqual(self.__class__.graphs.get_node(871).get_id(), (871, {'1': '2BIO3', '2': 'M'}), 'Check get_node')
