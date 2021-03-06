#! coding: utf-8
import io
import json
import os
import csv
import zipfile

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django_datajsonar.models import Field, Node

from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.dump.csv import CSVDumpGenerator
from series_tiempo_ar_api.apps.dump.models import CSVDumpTask
from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.utils import index_catalog


samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class CSVTest(TestCase):
    index = 'csv_dump_test_index'
    # noinspection PyUnresolvedReferences
    directory = os.path.join(settings.MEDIA_ROOT, 'test_dump')

    @classmethod
    def setUpClass(cls):
        super(CSVTest, cls).setUpClass()
        cls.catalog_id = 'csv_dump_test_catalog'
        path = os.path.join(samples_dir, 'distribution_daily_periodicity.json')
        index_catalog(cls.catalog_id, path, cls.index)
        cls.task = CSVDumpTask()
        cls.task.save()
        gen = CSVDumpGenerator(cls.task, index=cls.index, output_directory=cls.directory)
        gen.generate()

    def test_values_dump(self):
        file = self.task.dumpfile_set.get(file_name=constants.VALUES_CSV).file
        file.open('r')
        reader = csv.reader(file)
        next(reader)  # skip header
        row = next(reader)
        self.assertEqual(row[0], self.catalog_id)
        self.assertEqual(row[6], 'R/P1D')

    def test_values_length(self):
        file = self.task.dumpfile_set.get(file_name=constants.VALUES_CSV).file
        file.open('r')
        reader = csv.reader(file)
        header = next(reader)
        self.assertEqual(len(header), 7)

    def test_entity_identifiers(self):
        file = self.task.dumpfile_set.get(file_name=constants.VALUES_CSV).file
        file.open('r')
        reader = csv.reader(file)
        next(reader)

        row = next(reader)

        field_id = row[3]
        field = Field.objects.get(identifier=field_id)

        self.assertEqual(self.catalog_id, row[0])
        self.assertEqual(field.distribution.identifier, row[2])
        self.assertEqual(field.distribution.dataset.identifier, row[1])
        self.assertEqual(row[6], field.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)

    def test_full_csv_zipped(self):
        path = self.task.dumpfile_set.get(file_name=constants.FULL_CSV_ZIPPED).file.path
        csv_zipped = zipfile.ZipFile(path)

        # Necesario para abrir archivos zippeados en modo texto (no bytes)
        src_file = io.TextIOWrapper(csv_zipped.open(constants.FULL_CSV),
                                    encoding='utf8',
                                    newline='')
        reader = csv.reader(src_file)

        header = next(reader)

        self.assertEqual(len(header), 15)

    def test_full_csv_identifier_fields(self):
        file = self.task.dumpfile_set.get(file_name=constants.FULL_CSV).file
        file.open('r')
        reader = csv.reader(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])
        self.assertEqual(row[0], self.catalog_id)
        self.assertEqual(row[1], field.distribution.dataset.identifier)
        self.assertEqual(row[2], field.distribution.identifier)
        self.assertEqual(row[5], field.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)

    def test_full_csv_metadata_fields(self):
        file = self.task.dumpfile_set.get(file_name=constants.FULL_CSV).file
        file.open('r')
        reader = csv.reader(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])

        field_meta = json.loads(field.metadata)
        distribution_meta = json.loads(field.distribution.metadata)
        self.assertEqual(row[7], field.title)
        self.assertEqual(row[8], field_meta['units'])
        self.assertEqual(row[9], field_meta['description'])
        self.assertEqual(row[10], distribution_meta['description'])

    def test_full_csv_dataset_metadata_fields(self):
        file = self.task.dumpfile_set.get(file_name=constants.FULL_CSV).file
        file.open('r')
        reader = csv.reader(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])

        dataset_meta = json.loads(field.distribution.dataset.metadata)
        self.assertEqual(row[12], dataset_meta['publisher']['name'])
        self.assertEqual(row[13], dataset_meta['source'])
        self.assertEqual(row[14], field.distribution.dataset.title)

    def test_full_csv_dataset_theme_field(self):
        file = self.task.dumpfile_set.get(file_name=constants.FULL_CSV).file
        file.open('r')
        reader = csv.reader(file)
        next(reader)  # Header

        row = next(reader)

        field = Field.objects.get(identifier=row[3])

        dataset_meta = json.loads(field.distribution.dataset.metadata)

        themes = json.loads(Node.objects.get(catalog_id=self.catalog_id).catalog)['themeTaxonomy']

        theme_label = ''
        for theme in themes:
            if theme['id'] == dataset_meta['theme'][0]:
                theme_label = theme['label']
                break

        self.assertEqual(theme_label, row[11])

    @classmethod
    def tearDownClass(cls):
        ElasticInstance.get().indices.delete(cls.index)
        Node.objects.all().delete()


class CSVDumpCommandTests(TestCase):
    index = 'csv_dump_cmd_test_index'

    @classmethod
    def setUpClass(cls):
        super(CSVDumpCommandTests, cls).setUpClass()
        ElasticInstance.get().indices.create(cls.index)

    def setUp(self):
        CSVDumpTask.objects.all().delete()

    def test_command_creates_model(self):
        call_command('generate_dump', index=self.index)
        self.assertEqual(CSVDumpTask.objects.count(), 1)

        task = CSVDumpTask.objects.first()
        self.assertTrue(task.dumpfile_set.count(), task.logs)

    @classmethod
    def tearDownClass(cls):
        ElasticInstance.get().indices.delete(cls.index)
