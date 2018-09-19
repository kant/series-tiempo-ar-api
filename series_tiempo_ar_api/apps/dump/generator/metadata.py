import csv

from django.core.files import File
from iso8601 import iso8601

from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.generator.abstract_dump_gen import AbstractDumpGenerator
from series_tiempo_ar_api.apps.management import meta_keys


class MetadataCsvGenerator(AbstractDumpGenerator):

    rows = ['catalogo_id', 'dataset_id', 'distribucion_id', 'serie_id',
            'indice_tiempo_frecuencia', 'serie_titulo', 'serie_unidades',
            'serie_descripcion', 'distribucion_titulo', 'distribucion_descripcion',
            'dataset_responsable', 'dataset_fuente', 'dataset_titulo',
            'dataset_descripcion', 'serie_indice_inicio', 'serie_indice_final',
            'serie_valores_cant', 'serie_dias_no_cubiertos']

    def generate(self, filepath):

        with open(filepath, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.rows)

            writer.writeheader()
            for field, values in self.fields.items():
                writer.writerow(self.generate_row(field, values))

        with open(filepath, 'rb') as f:
            self.task.dumpfile_set.create(file_name=constants.METADATA_CSV, file=File(f))

    def generate_row(self, serie_name, values):
        dataset = values['dataset']
        distribution = values['distribution']
        serie = values['serie']

        return {
            self.rows[0]: dataset.catalog.identifier,
            self.rows[1]: dataset.identifier,
            self.rows[2]: distribution.identifier,
            self.rows[3]: serie_name,
            self.rows[4]: meta_keys.get(distribution, meta_keys.PERIODICITY),
            self.rows[5]: values['serie_titulo'],
            self.rows[6]: values['serie_unidades'],
            self.rows[7]: values['serie_descripcion'],
            self.rows[8]: values['distribucion_titulo'],
            self.rows[9]: values['distribucion_descripcion'],
            self.rows[10]: values['dataset_responsable'],
            self.rows[11]: values['dataset_fuente'],
            self.rows[12]: values['dataset_titulo'],
            self.rows[13]: values['dataset_descripcion'],
            self.rows[14]: meta_keys.get(serie, meta_keys.INDEX_START),
            self.rows[15]: meta_keys.get(serie, meta_keys.INDEX_END),
            self.rows[16]: meta_keys.get(serie, meta_keys.INDEX_SIZE),
            self.rows[17]: meta_keys.get(serie, meta_keys.DAYS_SINCE_LAST_UPDATE)
        }
