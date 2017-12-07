import unittest

import vtna.data_import as dimp
import vtna.graph as graph
import vtna.statistics as statistics


class TestFilterCreation(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
            cls.edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
            cls.temp_graph = graph.TemporalGraph(cls.edges, cls.meta, 20)

        def test_interactions_filter(self):
            self.assertEqual(statistics.statistics_interactions(TestFilterCreation.temp_graph, 4), 40,
                             'Number of interactions for one timestep')
            self.assertEqual(statistics.statistics_interactions(TestFilterCreation.temp_graph, 0, 4), 193,
                             'Number of interactions in a interval of two timesteps')
