# -*- coding: utf-8 -*-
from datetime import time

import mock
from django.test import TestCase

from series_tiempo_ar_api.apps.management.models import IndexingTaskCron


class CronTests(TestCase):

    def test_cron_added(self):
        mock_write = mock.Mock(return_value=None)
        cron = IndexingTaskCron(time='00:00:00')
        cron.cron_client.write = mock_write

        cron.save()

        self.assertTrue(cron.cron_client.crons)

    def test_cron_removed(self):
        mock_write = mock.Mock(return_value=None)
        cron = IndexingTaskCron(time='00:00:00')
        cron.cron_client.write = mock_write

        cron.save()
        self.assertTrue(cron.cron_client.crons)

        cron.delete()
        self.assertFalse(cron.cron_client.crons)

    def test_cron_scheduled_correctly(self):
        hour = 0
        minute = 0
        second = 0
        mock_write = mock.Mock(return_value=None)
        cron = IndexingTaskCron(time=time(hour=hour, minute=minute, second=second))
        cron.cron_client.write = mock_write

        cron.save()
        self.assertTrue(cron.cron_client.crons)

        job = cron.cron_client.crons[0]
        self.assertEqual(job.hour, hour)
        self.assertEqual(job.minute, minute)

    def test_cron_weekdays(self):

        mock_write = mock.Mock(return_value=None)
        cron = IndexingTaskCron(time='00:00:00', weekdays_only=True)
        cron.cron_client.write = mock_write

        cron.save()
        job = cron.cron_client.crons[0]
        self.assertEqual(job.dow, 'MON-FRI')
