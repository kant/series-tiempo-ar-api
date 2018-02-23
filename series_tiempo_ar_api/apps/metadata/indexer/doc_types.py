#!coding=utf8
from elasticsearch_dsl import DocType, Keyword, Text

from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class Field(DocType):
    """ Formato de los docs de metadatos a indexar en ES."""
    title = Keyword()
    description = Text()
    id = Keyword()
    dataset_title = Text()
    dataset_description = Text()
    theme_description = Text()
    units = Keyword()
    dataset_publisher_name = Keyword()

    # Guardamos una copia como keyword para poder usar en aggregations
    dataset_source = Text()
    dataset_source_keyword = Keyword()

    class Meta:
        index = constants.FIELDS_INDEX
        using = ElasticInstance.get()