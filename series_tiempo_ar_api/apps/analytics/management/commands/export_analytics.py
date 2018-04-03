#! coding: utf-8

from django.core.management import BaseCommand
from series_tiempo_ar_api.apps.analytics.tasks import export


class Command(BaseCommand):

    def handle(self, *args, **options):
        export.delay()
