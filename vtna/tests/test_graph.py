import unittest

import vtna.data_import as dimp
import vtna.graph as graph

class TestGraphCreation(unittest.TestCase):
        def test_number_of_graphs(self):
            meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
            edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
            graphs = graph.TemporalGraph(edges, meta, 20)

            self.assertEqual(len(graphs), 12, 'created all graphs')
