import unittest

import numpy as np

import vtna.graph
import vtna.statistics as stats


class TestGraphRelatedStatistics(unittest.TestCase):
        graphs = None
        edges = None
        update_delta = 20
        granularity = 40

        @classmethod
        def setUpClass(cls):
            # graphs:
            # 20: 1 <-> 2 <-> 3
            # 40: 1 <-> 2
            # 60: 1 <-> 2 <-> 3
            # 80: 6 <-> 8
            # 100: 6 <-> 8
            cls.graphs = [
                vtna.graph.Graph([
                    vtna.graph.Edge(1, 2, [20, 40]),
                    vtna.graph.Edge(2, 3, [20])
                ]),
                vtna.graph.Graph([
                    vtna.graph.Edge(1, 2, [60]),
                    vtna.graph.Edge(2, 3, [60]),
                    vtna.graph.Edge(6, 8, [80])
                ]),
                vtna.graph.Graph([
                    vtna.graph.Edge(6, 8, [100])
                ])
            ]
            cls.edges = [[20, 1, 2], [40, 1, 2], [20, 2, 3], [60, 1, 2], [60, 2, 3], [80, 6, 8], [100, 6, 8]]

        def test_total_edges_per_time_step_with_empty_iterable(self):
            self.assertEqual(stats.total_edges_per_time_step([]), [])

        def test_total_edges_per_time_step_with_toy_example(self):
            self.assertEqual(stats.total_edges_per_time_step(TestGraphRelatedStatistics.graphs), [3, 3, 1])

        def test_nodes_per_time_step_with_empty_iterable(self):
            self.assertEqual(stats.nodes_per_time_step([]), [])

        def test_nodes_per_time_step_with_toy_example(self):
            self.assertEqual(stats.nodes_per_time_step(TestGraphRelatedStatistics.graphs), [3, 5, 2])

        def test_multi_step_interactions_with_empty_iterable(self):
            self.assertEqual(stats.multi_step_interactions([], TestGraphRelatedStatistics.update_delta), {})

        def test_multi_step_interactions_with_toy_examples(self):
            interactions = stats.multi_step_interactions(TestGraphRelatedStatistics.graphs,
                                                         TestGraphRelatedStatistics.update_delta)
            self.assertEqual(interactions[(1, 2)], [(20, 60)])
            self.assertEqual(interactions[(2, 3)], [(20, 20), (60, 60)])
            self.assertEqual(interactions[(6, 8)], [(80, 100)])
            self.assertEqual(len(interactions.keys()), 3)

        def test_histogram_edges_with_empty_list(self):
            self.assertEqual(stats.histogram_edges([]), [])

        def test_histogram_edges_with_toy_examples(self):
            self.assertEqual(stats.histogram_edges(TestGraphRelatedStatistics.edges), [2, 1, 2, 1, 1])

        def test_histogram_edges_with_toy_examples_and_non_default_granularity(self):
            self.assertEqual(stats.histogram_edges(TestGraphRelatedStatistics.edges,
                                                   TestGraphRelatedStatistics.granularity), [3, 3, 1])


class TestAttributeRelatedStatistics(unittest.TestCase):
    nodes = None

    @classmethod
    def setUpClass(cls):
        cls.nodes = [
            vtna.graph.TemporalNode(1, {'fruit': 'apple', 'taste': 'good', 'price': 3.0}, 3),
            vtna.graph.TemporalNode(2, {'fruit': 'lemon', 'taste': 'average', 'price': 6.0}, 3),
            vtna.graph.TemporalNode(3, {'fruit': 'potato', 'taste': 'very good', 'price': 1.0}, 3),
            vtna.graph.TemporalNode(4, {'fruit': 'lemon', 'taste': 'good', 'price': 2.0}, 3),
        ]

    def test_mean_stdev_numeric_attribute_with_empty_iterable(self):
        with self.assertWarns(RuntimeWarning):
            self.assertTrue(np.all(np.isnan(stats.mean_stdev_numeric_attribute([], 'fruit'))))

    def test_mean_stdev_numeric_attribute_with_toy_example(self):
        mean, std = stats.mean_stdev_numeric_attribute(TestAttributeRelatedStatistics.nodes, 'price')
        self.assertAlmostEqual(mean, 3.0, places=4)
        self.assertAlmostEqual(std, 1.8708, places=4)

    def test_median_ordinal_attribute_with_toy_example(self):
        median = stats.median_ordinal_attribute(TestAttributeRelatedStatistics.nodes, 'taste',
                                                ['average', 'good', 'very good'])
        self.assertEqual(median, 'good')

    def test_mode_categorical_attribute_with_toy_example(self):
        fruit_mode = stats.mode_categorical_attribute(TestAttributeRelatedStatistics.nodes, 'fruit')
        self.assertEqual(fruit_mode, 'lemon')
        taste_mode = stats.mode_categorical_attribute(TestAttributeRelatedStatistics.nodes, 'taste')
        self.assertEqual(taste_mode, 'good')

    def test_histogram_categorical_attribute_with_toy_example(self):
        hist = stats.histogram_categorical_attribute(TestAttributeRelatedStatistics.nodes, 'fruit')
        self.assertEqual(hist['apple'], 1)
        self.assertEqual(hist['lemon'], 2)
        self.assertEqual(hist['potato'], 1)
        self.assertEqual(len(hist.keys()), 3)
