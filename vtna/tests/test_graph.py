import unittest

import vtna.data_import as dimp
import vtna.graph as graph


class TestGraphCreation(unittest.TestCase):
        temp_graph = None
        edges = None
        meta = None

        @classmethod
        def setUpClass(cls):
            cls.meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
            cls.edges = dimp.read_edge_table('vtna/tests/data/highschool_edges.ssv')
            cls.temp_graph = graph.TemporalGraph(cls.edges, cls.meta, 20)

        def test_number_of_graphs(self):
            self.assertEqual(len(TestGraphCreation.temp_graph), 13, 'created all graphs')

        def test_iterator_of_graphs(self):
            third_graph = None
            for idx, g in enumerate(TestGraphCreation.temp_graph):
                if idx == 2:
                    third_graph = g
                    break
            self.assertEqual(len(third_graph.get_edges()), 41)

        def test_get_edges(self):
            self.assertEqual(len(TestGraphCreation.temp_graph[1].get_edges()), 37, 'Check number of edges')

        def test_get_edge(self):
            self.assertEqual(TestGraphCreation.temp_graph[1].get_edge(122, 255).get_count(), 1,
                             'Check number of edge')
            self.assertEqual(TestGraphCreation.temp_graph[1].get_edge(122, 255).get_timestamps(), [1385982040],
                             'Check timestamps of edge')
            self.assertEqual(TestGraphCreation.temp_graph[1].get_edge(122, 255).get_incident_nodes(), (122, 255),
                             'Check incident nodes of edge')

        def test_number_of_nodes(self):
            self.assertEqual(len(TestGraphCreation.temp_graph.get_nodes()), 114, 'Correct node number')

        def test_get_node(self):
            self.assertEqual(TestGraphCreation.temp_graph.get_node(871).get_id(), 871, 'Check node_id')

        def test_global_attributes(self):
            self.assertEqual(TestGraphCreation.temp_graph.get_node(871).get_global_attribute('1'), '2BIO3',
                             'Check get_global_attribute')
            TestGraphCreation.temp_graph.get_node(871).update_global_attribute('1', 'test')
            self.assertEqual(TestGraphCreation.temp_graph.get_node(871).get_global_attribute('1'), 'test',
                             'Check get_global_attribute with overridden attribute')

        def test_local_attributes(self):
            TestGraphCreation.temp_graph.get_node(871).update_local_attribute('1', [str(i) for i in range(13)])
            self.assertEqual(TestGraphCreation.temp_graph.get_node(871).get_local_attribute('1', 0), '0',
                             'Check get_local_attribute with type string')
            self.assertEqual(TestGraphCreation.temp_graph.get_node(871).get_local_attribute('1', 2), '2',
                             'Check get_local_attribute with type int')

        def test_with_higher_granularity(self):
            graphs_high_granularity = graph.TemporalGraph(TestGraphCreation.edges, TestGraphCreation.meta, 60)
            self.assertEqual(len(graphs_high_granularity), 5, 'created all graphs')
            self.assertEqual(graphs_high_granularity[0].get_edge(122, 255).get_count(), 3, 'Check number of edge')

        def test_create_graph_without_metadata(self):
            temp_graph = graph.TemporalGraph(TestGraphCreation.edges, None, 20)
            self.assertTrue(len(temp_graph.get_nodes()) > 0)
            with self.assertRaises(KeyError):
                temp_graph.get_node(454).get_global_attribute('1')

        def test_create_graph_with_invalid_metadata(self):
            invalid_meta = dimp.MetadataTable('vtna/tests/data/invalid_metadata.csv')
            with self.assertRaises(graph.MissingNodesInMetadataError):
                graph.TemporalGraph(self.edges, invalid_meta, 20)


class TestAccumulatedGraph(unittest.TestCase):
    edges1 = None
    edges2 = None

    @classmethod
    def setUpClass(cls):
        cls.edges1 = [
            (0, 1, 2),
            (20, 2, 3),
            (40, 2, 3),
            (60, 2, 3),
            (60, 4, 6)
        ]

        cls.edges2 = [
            (0, 1, 2),
            (20, 2, 3),
            (60, 3, 4),
            (100, 4, 5)
        ]

    def test_set_get_cumulative_mode(self):
        temp_graph = graph.TemporalGraph(TestAccumulatedGraph.edges1, None, 20)
        self.assertFalse(temp_graph.is_cumulative())
        temp_graph.set_cumulative(True)
        self.assertTrue(temp_graph.is_cumulative())
        temp_graph.set_cumulative(False)
        self.assertFalse(temp_graph.is_cumulative())

    def test_accumulated_with_cont_example(self):
        temp_graph = graph.TemporalGraph(TestAccumulatedGraph.edges1, None, 20)
        temp_graph.set_cumulative(True)
        graphs = list(temp_graph.__iter__())
        self.assertEqual(len(graphs[0].get_edges()), 1)
        self.assertEqual(len(graphs[1].get_edges()), 2)
        self.assertEqual(len(graphs[2].get_edges()), 2)
        self.assertEqual(len(graphs[3].get_edges()), 3)

    def test_accumulated_with_gap_example(self):
        temp_graph = graph.TemporalGraph(TestAccumulatedGraph.edges2, None, 20)
        temp_graph.set_cumulative(True)
        graphs = list(temp_graph.__iter__())
        self.assertEqual(len(graphs[0].get_edges()), 1)
        self.assertEqual(len(graphs[1].get_edges()), 2)
        self.assertEqual(len(graphs[2].get_edges()), 2)
        self.assertEqual(len(graphs[3].get_edges()), 3)
        self.assertEqual(len(graphs[4].get_edges()), 3)
        self.assertEqual(len(graphs[5].get_edges()), 4)

    def test_switch_on_off_cumulative_graph_with_cont_example(self):
        # Multiple on-offs to control for the fact that the cumulative graph is only computed on activation via set
        temp_graph = graph.TemporalGraph(TestAccumulatedGraph.edges1, None, 20)
        graphs = list(temp_graph.__iter__())
        self.assertEqual(len(graphs[0].get_edges()), 1)
        self.assertEqual(len(graphs[1].get_edges()), 1)
        self.assertEqual(len(graphs[2].get_edges()), 1)
        self.assertEqual(len(graphs[3].get_edges()), 2)
        temp_graph.set_cumulative(True)
        graphs = list(temp_graph.__iter__())
        self.assertEqual(len(graphs[0].get_edges()), 1)
        self.assertEqual(len(graphs[1].get_edges()), 2)
        self.assertEqual(len(graphs[2].get_edges()), 2)
        self.assertEqual(len(graphs[3].get_edges()), 3)
        temp_graph.set_cumulative(False)
        graphs = list(temp_graph.__iter__())
        self.assertEqual(len(graphs[0].get_edges()), 1)
        self.assertEqual(len(graphs[1].get_edges()), 1)
        self.assertEqual(len(graphs[2].get_edges()), 1)
        self.assertEqual(len(graphs[3].get_edges()), 2)
        temp_graph.set_cumulative(True)
        graphs = list(temp_graph.__iter__())
        self.assertEqual(len(graphs[0].get_edges()), 1)
        self.assertEqual(len(graphs[1].get_edges()), 2)
        self.assertEqual(len(graphs[2].get_edges()), 2)
        self.assertEqual(len(graphs[3].get_edges()), 3)
