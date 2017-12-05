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
        super(TestTemporalEdgeTableGetItem, cls).setUpClass()
        cls.edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')

    def test_earliest_timestamp_int(self):
        edges = list(TestTemporalEdgeTableGetItem.edges[1385982020])
        unique_timestamps = list(set(timestamp for timestamp, *_ in edges))

        self.assertEqual(len(edges), 35, 'correct number of edges returned')
        self.assertEqual(len(unique_timestamps), 1, 'only 1 timestamps returned')
        self.assertEqual(unique_timestamps[0], 1385982020, 'correct timestamp returned')

    def test_none_none_slice(self):
        earliest = TestTemporalEdgeTableGetItem.edges.get_earliest_timestamp()
        latest = TestTemporalEdgeTableGetItem.edges.get_latest_timestamp()
        edges = list(TestTemporalEdgeTableGetItem.edges[:])
        unique_timestamps = set(timestamp for timestamp, *_ in edges)

        self.assertEqual(min(unique_timestamps), earliest, 'contains earliest timestamp')
        self.assertEqual(max(unique_timestamps), latest, 'contains latest timestamp')
        self.assertEqual(len(edges), 500, 'correct number of edges returned')

    def test_none_max_slice(self):
        earliest = TestTemporalEdgeTableGetItem.edges.get_earliest_timestamp()
        latest = TestTemporalEdgeTableGetItem.edges.get_latest_timestamp()
        edges = list(TestTemporalEdgeTableGetItem.edges[:latest])
        unique_timestamps = set(timestamp for timestamp, *_ in edges)

        self.assertEqual(min(unique_timestamps), earliest, 'contains earliest timestamp')
        self.assertEqual(len(edges), 497, 'correct number of edges returned')
        self.assertTrue(latest not in unique_timestamps, 'does not contains latest timestamp')

    def test_bad_type_int(self):
        with self.assertRaises(TypeError):
            _ = TestTemporalEdgeTableGetItem.edges[3.14]
        with self.assertRaises(TypeError):
            _ = TestTemporalEdgeTableGetItem.edges['foo']
        with self.assertRaises(TypeError):
            _ = TestTemporalEdgeTableGetItem.edges[int]

    def test_bad_type_slice(self):
        with self.assertRaises(TypeError):
            _ = TestTemporalEdgeTableGetItem.edges[3.14:]
        with self.assertRaises(TypeError):
            _ = TestTemporalEdgeTableGetItem.edges[:'foo']
        with self.assertRaises(TypeError):
            _ = TestTemporalEdgeTableGetItem.edges[True:int]


class TestMetadataTableFunctionality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestMetadataTableFunctionality, cls).setUpClass()
        cls.meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')

    def test_get_attribute_names(self):
        names = TestMetadataTableFunctionality.meta.get_attribute_names()
        self.assertEqual(names, {'1', '2'}, 'names are initially "1" and "2"')

    def test_rename_attribute_names(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        meta.rename_attributes({'1': 'class', '2': 'gender'})
        self.assertEqual(meta.get_attribute_names(), {'class', 'gender'})

    def test_get_categories(self):
        cat2 = TestMetadataTableFunctionality.meta.get_categories('2')
        self.assertEqual(set(cat2), {'F', 'M', 'Unknown'}, 'correct categories returned')
        self.assertEqual(len(cat2), 3, 'unique categories returned')

    def test_order_categories(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        self.assertFalse(meta.is_ordered('1'), 'check category is unsorted initially')
        order = ['2BIO1', '2BIO2', '2BIO3', 'MP', 'MP*1', 'MP*2', 'PC', 'PC*', 'PSI*']
        meta.order_categories('1', order)
        self.assertEqual(meta.get_categories('1'), order)
        self.assertTrue(meta.is_ordered('1'))

    def test_order_categories_with_one_missing_category(self):
        with self.assertRaises(dimp.BadOrderError):
            TestMetadataTableFunctionality.meta.order_categories('1', ['2BIO1', '2BIO2', '2BIO3', 'MP', 'MP*1', 'MP*2',
                                                                       'PC', 'PC*'])

    def test_order_categories_with_too_many_categories(self):
        with self.assertRaises(dimp.BadOrderError):
            TestMetadataTableFunctionality.meta.order_categories('1', ['2BIO1', '2BIO2', '2BIO3', 'MP', 'MP*1', 'MP*2',
                                                                       'PC', 'PC*', 'PSI*', 'PSI'])

    def test_order_categories_with_wrong_category(self):
        with self.assertRaises(dimp.BadOrderError):
            TestMetadataTableFunctionality.meta.order_categories('1', ['Cake', '2BIO2', '2BIO3', 'MP', 'MP*1', 'MP*2',
                                                                       'PC', 'PC*', 'PSI*'])

    def test_remove_order(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        self.assertFalse(meta.is_ordered('1'), 'check category is unsorted initially')
        order = ['2BIO1', '2BIO2', '2BIO3', 'MP', 'MP*1', 'MP*2', 'PC', 'PC*', 'PSI*']
        meta.order_categories('1', order)
        self.assertTrue(meta.is_ordered('1'))
        meta.remove_order('1')
        self.assertFalse(meta.is_ordered('1'), 'category is unordered after calling remove order')

    def test_getitem_with_bad_type(self):
        with self.assertRaises(TypeError):
            _ = TestMetadataTableFunctionality.meta['72']

    def test_getitem_with_not_existing_key(self):
        with self.assertRaises(KeyError):
            _ = TestMetadataTableFunctionality.meta[73]

    def test_getitem_with_valid_key(self):
        attributes = TestMetadataTableFunctionality.meta[72]
        self.assertEqual(attributes['1'], '2BIO1', 'correct first attribute')
        self.assertEqual(attributes['2'], 'F', 'correct second attribute')

    def test_keys(self):
        self.assertEqual(len(TestMetadataTableFunctionality.meta.keys()), 114)

    def test_values(self):
        self.assertEqual(len(TestMetadataTableFunctionality.meta.values()), 114)

    def test_items(self):
        self.assertEqual(len(TestMetadataTableFunctionality.meta.items()), 114)
