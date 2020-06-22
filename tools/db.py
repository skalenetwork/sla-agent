#   -*- coding: utf-8 -*-
#
#   This file is part of sla-agent
#
#   Copyright (C) 2019-Present SKALE Labs
#
#   sla-agent is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   sla-agent is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with sla-agent.  If not, see <https://www.gnu.org/licenses/>.


import logging

from configs.db import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from peewee import BooleanField, DateTimeField, IntegerField, Model, MySQLDatabase, fn

logger = logging.getLogger(__name__)


dbhandle = MySQLDatabase(
    DB_NAME, user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


class BaseModel(Model):
    class Meta:
        database = dbhandle


class Report(BaseModel):
    my_id = IntegerField()
    target_id = IntegerField()
    is_offline = BooleanField()
    latency = IntegerField()
    stamp = DateTimeField()


@dbhandle.connection_context()
def save_metrics_to_db(my_id, target_id, is_offline, latency):
    """Save metrics (downtime and latency) to database."""
    report = Report(my_id=my_id,
                    target_id=target_id,
                    is_offline=is_offline,
                    latency=latency)
    report.save()


@dbhandle.connection_context()
def get_month_metrics_for_node(my_id, target_id, start_date, end_date) -> dict:
    """Returns a dict with aggregated month metrics - downtime and latency."""

    downtime_results = Report.select(
        fn.SUM(
            Report.is_offline).alias('sum')).where(
        (Report.my_id == my_id) & (
                Report.target_id == target_id) & (
            Report.stamp >= start_date) & (
            Report.stamp <= end_date))

    latency_results = Report.select(
        fn.AVG(
            Report.latency).alias('avg')).where(
        (Report.my_id == my_id) & (
                Report.target_id == target_id) & (
            Report.stamp >= start_date) & (
            Report.stamp <= end_date) & (
            Report.latency >= 0))
    downtime = int(
        downtime_results[0].sum) if downtime_results[0].sum is not None else 0
    latency = latency_results[0].avg if latency_results[0].avg is not None else 0
    return {'downtime': downtime, 'latency': latency}


@dbhandle.connection_context()
def clear_all_reports():
    nrows = Report.delete().execute()
    logger.info(f'{nrows} records deleted')


# @dbhandle.connection_context()
# def clear_all_report_events():
#     nrows = ReportEvent.delete().execute()
#     logger.info(f'{nrows} records deleted')


@dbhandle.connection_context()
def get_count_of_report_records():
    return Report.select().count()


# @dbhandle.connection_context()
# def get_count_of_report_events_records():
#     return ReportEvent.select().count()
