#! coding: utf-8
import logging

from django_rq import job

from elasticsearch_dsl import Index
from django_datajsonar.models import Node
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from .doc_types import Field
from .catalog_meta_indexer import CatalogMetadataIndexer
from .index import get_fields_meta_index

logger = logging.getLogger(__name__)


class MetadataIndexer:

    def __init__(self, task, doc_type=Field, index: Index = None):
        self.task = task
        self.index = index if index is not None else get_fields_meta_index()
        self.doc_type = doc_type

    def setup_index(self):
        """Borra y regenera el índice entero. Esto es 'safe' porque
        todos los datos a indexar en este índice están guardados en
        la base de datos relacional
        """
        if self.index.exists():
            self.index.delete()
        self.index.doc_type(self.doc_type)
        self.index.create()

    def run(self):
        self.setup_index()
        for node in Node.objects.filter(indexable=True):
            try:
                IndexMetadataTask.info(self.task,
                                       u'Inicio de la indexación de metadatos de {}'
                                       .format(node.catalog_id))
                CatalogMetadataIndexer(node, self.task, self.doc_type).index()
                IndexMetadataTask.info(self.task, u'Fin de la indexación de metadatos de {}'
                                       .format(node.catalog_id))

            except Exception as e:
                IndexMetadataTask.info(self.task,
                                       u'Error en la lectura del catálogo {}: {}'.format(node.catalog_id, e))

        self.index.forcemerge()


@job('indexing', timeout=10000)
def run_metadata_indexer(task):
    MetadataIndexer(task).run()
    task.refresh_from_db()
    task.status = task.FINISHED
    task.save()
