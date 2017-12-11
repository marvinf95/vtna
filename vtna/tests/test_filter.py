import unittest

import vtna.graph
import vtna.filter


class TestFilterCreation(unittest.TestCase):
        nodes = None
        degree_order = None

        @classmethod
        def setUpClass(cls):
            cls.nodes = [
                vtna.graph.TemporalNode(1, {'Gender': 'Female', 'Degree': 'Master'}, 42),
                vtna.graph.TemporalNode(3, {'Gender': 'Unknown', 'Degree': 'Bachelor'}, 42),
                vtna.graph.TemporalNode(42, {'Gender': 'Male', 'Degree': 'Highschool'}, 42)
            ]
            cls.degree_order = ['None', 'Highschool', 'Bachelor', 'Master', 'Doctorate']

        def test_categorical_attribute_equal(self):
            pred = vtna.filter.categorical_attribute_equal('Gender', 'Unknown')
            self.assertTrue(pred(TestFilterCreation.nodes[1]))
            self.assertFalse(pred(TestFilterCreation.nodes[0]))

        def test_ordinal_attribute_greater_than_equal(self):
            pred = vtna.filter.ordinal_attribute_greater_than_equal('Degree', 'Bachelor',
                                                                    TestFilterCreation.degree_order)
            self.assertTrue(pred(TestFilterCreation.nodes[0]))
            self.assertTrue(pred(TestFilterCreation.nodes[1]))
            self.assertFalse(pred(TestFilterCreation.nodes[2]))

        def test_ordinal_attribute_greater_than(self):
            pred = vtna.filter.ordinal_attribute_greater_than('Degree', 'Bachelor',
                                                              TestFilterCreation.degree_order)
            self.assertTrue(pred(TestFilterCreation.nodes[0]))
            self.assertFalse(pred(TestFilterCreation.nodes[1]))
            self.assertFalse(pred(TestFilterCreation.nodes[2]))

        def test_node_filter_call(self):
            pred = vtna.filter.categorical_attribute_equal('Gender', 'Unknown')
            has_unknown_gender = vtna.filter.NodeFilter(pred)
            results = list(has_unknown_gender(TestFilterCreation.nodes))
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].get_id(), 3)

        def test_node_filter_add(self):
            unknown_pred = vtna.filter.categorical_attribute_equal('Gender', 'Unknown')
            female_pred = vtna.filter.categorical_attribute_equal('Gender', 'Female')
            union_filter = vtna.filter.NodeFilter(unknown_pred) + vtna.filter.NodeFilter(female_pred)
            results = list(union_filter(TestFilterCreation.nodes))
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].get_id(), 1)
            self.assertEqual(results[1].get_id(), 3)

        def test_node_filter_multiply(self):
            unknown_pred = vtna.filter.categorical_attribute_equal('Gender', 'Unknown')
            female_pred = vtna.filter.categorical_attribute_equal('Gender', 'Female')
            union_filter = vtna.filter.NodeFilter(unknown_pred) * vtna.filter.NodeFilter(female_pred)
            results = list(union_filter(TestFilterCreation.nodes))
            self.assertEqual(len(results), 0)

        def test_node_filter_subtract(self):
            female_pred = vtna.filter.categorical_attribute_equal('Gender', 'Female')
            union_filter = vtna.filter.NodeFilter(lambda n: True) - vtna.filter.NodeFilter(female_pred)
            results = list(union_filter(TestFilterCreation.nodes))
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].get_id(), 3)
            self.assertEqual(results[1].get_id(), 42)

        def test_node_filter_negation(self):
            female_pred = vtna.filter.categorical_attribute_equal('Gender', 'Female')
            union_filter = - vtna.filter.NodeFilter(female_pred)
            results = list(union_filter(TestFilterCreation.nodes))
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].get_id(), 3)
            self.assertEqual(results[1].get_id(), 42)

        def test_node_filter_add_bad_type(self):
            with self.assertRaises(TypeError):
                vtna.filter.NodeFilter(lambda n: True) + 'false type'

        def test_node_filter_multiply_bad_type(self):
            with self.assertRaises(TypeError):
                vtna.filter.NodeFilter(lambda n: True) * 'false type'

        def test_node_filter_subtract_bad_type(self):
            with self.assertRaises(TypeError):
                vtna.filter.NodeFilter(lambda n: True) - 'false type'
