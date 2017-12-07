import unittest

from nose.tools import raises

import vtna.node_measure as nome
import vtna.data_import as dimp
import vtna.graph as graph

from numbers import Number


class TestCentralityMeasures(unittest.TestCase):
    def setUp(self):
        edge_table = dimp.TemporalEdgeTable(
            'vtna/tests/data/highschool_edges.ssv')
        self._temp_graph = graph.TemporalGraph(edge_table, None, 40)
        self._timestep_count = len(self._temp_graph)

    def test_local_degree_centrality(self):
        centrality = nome.LocalDegreeCentrality(self._temp_graph)
        self.assertIsNotNone(centrality.get_description())
        centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            # Test length of measure timestep list == timesteps in graph
            self.assertEqual(len(centrality[node.get_id()]),
                             self._timestep_count)
            # Test the centralities of first, second and last timesteps
            for test_timestamp in [0, 1, self._timestep_count - 1]:
                # Get the centrality as attribute
                att_cent = node.get_local_attribute(centrality.get_name(),
                                                    test_timestamp)
                # Test type of centrality
                self.assertIsInstance(att_cent, Number, f"type(att_cent)="
                                                        f"{type(att_cent)}")
                # Test class member centrality == attribute centrality
                self.assertEqual(centrality[node.get_id()][test_timestamp],
                                 att_cent)
                # This test depends on if the current node exists n the graph:
                for edge in self._temp_graph[test_timestamp].get_edges():
                    if edge.get_incident_nodes()[0] == node.get_id() or \
                            edge.get_incident_nodes()[1] == node.get_id():
                        # If it exists, its measure must be greater than 0
                        self.assertGreater(att_cent, 0, f"Failed for node "
                                                        f"{node.get_id()}, "
                                                        f"timestep "
                                                        f"{test_timestamp}")
                        break
                else:
                    # Otherwise the measure must be 0
                    self.assertEqual(att_cent, 0)

    def test_global_degree_centrality(self):
        centrality = nome.GlobalDegreeCentrality(self._temp_graph)
        self.assertIsNotNone(centrality.get_description())
        centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            # Get the centrality as attribute
            att_cent = node.get_global_attribute(centrality.get_name())
            # Test type of centrality
            self.assertIsInstance(att_cent, Number, f"type(att_cent)="
                                                    f"{type(att_cent)}")
            # Test class member centrality == attribute centrality
            self.assertEqual(centrality[node.get_id()], att_cent)
            # If it exists, its measure must be greater than 0
            self.assertGreater(att_cent, 0, f"Failed for node {node.get_id()}")

    def test_local_betweenness_centrality(self):
        centrality = nome.LocalBetweennessCentrality(self._temp_graph)
        self.assertIsNotNone(centrality.get_description())
        centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            # Test length of measure timestep list == timesteps in graph
            self.assertEqual(len(centrality[node.get_id()]),
                             self._timestep_count)
            # Test the centralities of first, second and last timesteps
            for test_timestamp in [0, 1, self._timestep_count - 1]:
                # Get the centrality as attribute
                att_cent = node.get_local_attribute(centrality.get_name(),
                                                    test_timestamp)
                # Test type of centrality
                self.assertIsInstance(att_cent, Number, f"type(att_cent)="
                                                        f"{type(att_cent)}")
                # Test class member centrality == attribute centrality
                self.assertEqual(centrality[node.get_id()][test_timestamp],
                                 att_cent)
                # This test depends if the node exists in the current graph:
                for edge in self._temp_graph[test_timestamp].get_edges():
                    if edge.get_incident_nodes()[0] == node.get_id() or \
                            edge.get_incident_nodes()[1] == node.get_id():
                        break
                else:
                    # If it doesn't the measure must be 0
                    self.assertEqual(att_cent, 0)

    def test_global_betweenness_centrality(self):
        centrality = nome.GlobalBetweennessCentrality(self._temp_graph)
        self.assertIsNotNone(centrality.get_description())
        centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            # Get the centrality as attribute
            att_cent = node.get_global_attribute(centrality.get_name())
            # Test type of centrality
            self.assertIsInstance(att_cent, Number, f"type(att_cent)="
                                                    f"{type(att_cent)}")
            # Test class member centrality == attribute centrality
            self.assertEqual(centrality[node.get_id()], att_cent)

    def test_local_closeness_centrality(self):
        centrality = nome.LocalClosenessCentrality(self._temp_graph)
        self.assertIsNotNone(centrality.get_description())
        centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            # Test length of measure timestep list == timesteps in graph
            self.assertEqual(len(centrality[node.get_id()]),
                             self._timestep_count)
            # Test the centralities of first, second and last timesteps
            for test_timestamp in [0, 1, self._timestep_count - 1]:
                # Get the centrality as attribute
                att_cent = node.get_local_attribute(centrality.get_name(),
                                                    test_timestamp)
                # Test type of centrality
                self.assertIsInstance(att_cent, Number, f"type(att_cent)="
                                                        f"{type(att_cent)}")
                # Test class member centrality == attribute centrality
                self.assertEqual(centrality[node.get_id()][test_timestamp],
                                 att_cent)
                # This test depends on if the current node exists n the graph:
                for edge in self._temp_graph[test_timestamp].get_edges():
                    if edge.get_incident_nodes()[0] == node.get_id() or \
                            edge.get_incident_nodes()[1] == node.get_id():
                        # If it exists, its measure must be greater than 0
                        self.assertGreater(att_cent, 0, f"Failed for node "
                                                        f"{node.get_id()}, "
                                                        f"timestep "
                                                        f"{test_timestamp}")
                        break
                else:
                    # Otherwise the measure must be 0
                    self.assertEqual(att_cent, 0)
        i = 1 / 0

    def test_global_closeness_centrality(self):
        centrality = nome.GlobalClosenessCentrality(self._temp_graph)
        self.assertIsNotNone(centrality.get_description())
        centrality.add_to_graph()
        for node in self._temp_graph.get_nodes():
            # Get the centrality as attribute
            att_cent = node.get_global_attribute(centrality.get_name())
            # Test type of centrality
            self.assertIsInstance(att_cent, Number, f"type(att_cent)="
                                                    f"{type(att_cent)}")
            # Test class member centrality == attribute centrality
            self.assertEqual(centrality[node.get_id()], att_cent)
            # If it exists, its measure must be greater than 0
            self.assertGreater(att_cent, 0, f"Failed for node {node.get_id()}")

    @raises(TypeError)
    def test_lbc_getitem_invalid_parameter(self):
        nome.LocalDegreeCentrality(self._temp_graph).__getitem__(
            "NotAnInteger")

    @raises(TypeError)
    def test_gcc_getitem_invalid_parameter(self):
        nome.GlobalClosenessCentrality(self._temp_graph).__getitem__(
            "NotAnInteger")

    @raises(TypeError)
    def test_lbc_init_invalid_parameter(self):
        nome.LocalDegreeCentrality(self._temp_graph).__init__(
            "NotATemporalGraph")
