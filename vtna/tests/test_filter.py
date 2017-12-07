import unittest

import vtna.data_import as dimp
import vtna.graph as graph
import vtna.filter as filter


class TestFilterCreation(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
            cls.edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
            cls.temp_graph = graph.TemporalGraph(cls.edges, cls.meta, 20)

        def test_attribute_filter(self):
            self.assertEqual(len(filter.filter_attributes(TestFilterCreation.temp_graph, '1','PC')), 3, 'Check number of node_ids for Attribute filter')