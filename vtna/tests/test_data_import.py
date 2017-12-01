import unittest

import vtna.data_import as dimp


class TestImportFromDifferentSources(unittest.TestCase):

    def test_import_metadata_from_raw_text(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')

        self.assertEqual(len(meta.keys()), 114, 'loaded all nodes')
        self.assertEqual(len(meta.get_attribute_names()), 2, 'loaded all columns')

    def test_import_edgedata_from_raw_text(self):
        edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')

        self.assertEqual(edges.get_earliest_timestamp(), 1385982020, 'determined earliest timestamp')
        self.assertEqual(edges.get_latest_timestamp(), 1385982260, 'determined latest timestamp')
        self.assertEqual(edges.get_update_delta(), 20, 'inferred minimum update time interval')
