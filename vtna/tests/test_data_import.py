import unittest

import vtna.data_import as dimp


class TestEdgeListUtilities(unittest.TestCase):
    edges = None

    @classmethod
    def setUpClass(cls):
        super(TestEdgeListUtilities, cls).setUpClass()
        cls.edges = [(40, 1, 2), (60, 1, 2), (100, 3, 4), (100, 1, 2), (180, 3, 4)]

    def test_get_time_interval_of_edges(self):
        earliest, latest = dimp.get_time_interval_of_edges(TestEdgeListUtilities.edges)
        self.assertEqual(earliest, 40)
        self.assertEqual(latest, 180)

    def test_get_time_interval_of_edges_empty_parameter(self):
        with self.assertRaises(ValueError):
            dimp.get_time_interval_of_edges(list())

    def test_infer_update_delta(self):
        update_delta = dimp.infer_update_delta(TestEdgeListUtilities.edges)
        self.assertEqual(update_delta, 20)

    def test_inter_update_delta_empty_parameter(self):
        with self.assertRaises(ValueError):
            dimp.infer_update_delta(list())

    def test_group_edges_by_granularity(self):
        buckets = dimp.group_edges_by_granularity(TestEdgeListUtilities.edges, 40)
        self.assertEqual(len(buckets), 4, 'correct number of groups')
        self.assertEqual(len(buckets[0]), 2)
        self.assertEqual(len(buckets[1]), 2)
        self.assertEqual(len(buckets[2]), 0)
        self.assertEqual(len(buckets[3]), 1)


class TestImportFromDifferentSources(unittest.TestCase):
    def test_import_metadata_from_raw_text(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')

        self.assertEqual(len(meta.keys()), 114, 'loaded all nodes')
        self.assertEqual(len(meta.get_attribute_names()), 2, 'loaded all columns')

    def test_import_edgedata_from_raw_text(self):
        edges = dimp.read_edge_table('vtna/tests/data/highschool_edges.ssv')
        self.__test_imported_edge_data(edges)

    def test_import_edgedata_from_bz2(self):
        edges = dimp.read_edge_table('vtna/tests/data/highschool_edges.ssv.bz2')
        self.__test_imported_edge_data(edges)

    def test_import_edgedata_from_gz(self):
        edges = dimp.read_edge_table('vtna/tests/data/highschool_edges.ssv.gz')
        self.__test_imported_edge_data(edges)

    def __test_imported_edge_data(self, edges):
        earliest, latest = dimp.get_time_interval_of_edges(edges)
        update_delta = dimp.infer_update_delta(edges)
        self.assertEqual(earliest, 1385982020, 'determined earliest timestamp')
        self.assertEqual(latest, 1385982260, 'determined latest timestamp')
        self.assertEqual(update_delta, 20, 'inferred minimum update time interval')


class TestMetadataTableFunctionality(unittest.TestCase):
    meta = None

    @classmethod
    def setUpClass(cls):
        super(TestMetadataTableFunctionality, cls).setUpClass()
        cls.meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')

    def test_get_attribute_names(self):
        names = TestMetadataTableFunctionality.meta.get_attribute_names()
        self.assertEqual(set(names), {'1', '2'}, 'names are initially "1" and "2"')

    def test_rename_attribute_names(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        meta.rename_attributes({'1': 'class', '2': 'gender'})
        self.assertEqual(set(meta.get_attribute_names()), {'class', 'gender'})

    def test_rename_attribute_names_duplicates(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        with self.assertRaises(dimp.DuplicateTargetNamesError):
            meta.rename_attributes({'1': 'class', '2': 'class'})

    def test_rename_attribute_names_illegal(self):
        meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
        meta.rename_attributes({'1': 'class'})
        with self.assertRaises(dimp.RenamingTargetExistsError):
            meta.rename_attributes({'2': 'class'})

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
