import unittest

import vtna.data_import as dimp


class TestImportFromDifferentSources(unittest.TestCase):

    def test_import_metadata_from_raw_text(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')

        self.assertEqual(len(meta.keys()), 114, 'loaded all nodes')
        self.assertEqual(len(meta.get_attribute_names()), 2, 'loaded all columns')

    def test_import_edgedata_from_raw_text(self):
        edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
        self.__test_imported_edge_data(edges)

    def test_import_edgedata_from_bz2(self):
        edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv.bz2')
        self.__test_imported_edge_data(edges)

    def test_import_edgedata_from_gz(self):
        edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv.gz')
        self.__test_imported_edge_data(edges)

    def __test_imported_edge_data(self, edges):
        self.assertEqual(edges.get_earliest_timestamp(), 1385982020, 'determined earliest timestamp')
        self.assertEqual(edges.get_latest_timestamp(), 1385982260, 'determined latest timestamp')
        self.assertEqual(edges.get_update_delta(), 20, 'inferred minimum update time interval')


class TestTemporalEdgeTableGetItem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for each test use setUpClass()
            and store the result as class variable
        """
        super(TestTemporalEdgeTableGetItem, cls).setUpClass()
        cls.edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')

    def test_earliest_timestamp_int(self):
        edges = list(TestTemporalEdgeTableGetItem.edges[1385982020])

        self.assertEqual(len(edges), 35, 'correct number of edges returned')
        unique_timestamps = list(set(timestamp for timestamp, *_ in edges))
        self.assertEqual(len(unique_timestamps), 1, 'only 1 timestamps returned')
        self.assertEqual(unique_timestamps[0], 1385982020, 'correct timestamp returned')

    def test_none_none_slice(self):
        edges = list(TestTemporalEdgeTableGetItem.edges[:])
        unique_timestamps = set(timestamp for timestamp, *_ in edges)
        self.assertEqual(min(unique_timestamps), 1385982020, 'contains earliest timestamp')
        self.assertEqual(max(unique_timestamps), 1385982260, 'contains latest timestamp')
        self.assertEqual(len(edges), 500, 'correct number of edges returned')

