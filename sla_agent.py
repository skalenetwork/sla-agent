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

"""
SLA agent runs on every node of SKALE network, periodically gets a list of nodes to validate
from SKALE Manager (SM), checks its health metrics and sends transactions with average metrics to SM
when it's time to send it
"""
import concurrent.futures
import json
import logging
import queue
import socket
import threading
import time
from datetime import datetime
import random
import schedule
from skale.manager_client import spawn_skale_lib
from skale.transactions.result import TransactionError

from configs import LONG_LINE, MONITOR_PERIOD, NODE_CONFIG_FILEPATH, REPORT_PERIOD
from tools import db
from tools.helper import (
    MsgIcon, Notifier, call_retry, check_if_node_is_registered, check_required_balance,
    get_id_from_config, init_skale)
from tools.logger import init_agent_logger
from tools.metrics import get_metrics_for_node

MONITORED_NODES_FILEPATH = 'monitored_nodes.json'
MONITORED_NODES_COUNT = 24
DISABLE_REPORTING = True


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


class Worker:

    def __init__(self):
        self.jobqueue = queue.Queue()

    def worker(self):
        while True:
            job_func = self.jobqueue.get()
            job_func()
            self.jobqueue.task_done()


class Monitor:

    def __init__(self, skale, node_id=None):
        self.agent_name = self.__class__.__name__.lower()
        init_agent_logger(self.agent_name, node_id)
        self.logger = logging.getLogger(self.agent_name)

        # Hide skale init log output
        init_skale_logger = logging.getLogger('skale.manager_client')
        init_skale_logger.setLevel(logging.WARNING)

        self.logger.info(f'Initialization of {self.agent_name} started...')
        if node_id is None:
            self.id = get_id_from_config(NODE_CONFIG_FILEPATH)
            self.is_test_mode = False
        else:
            self.id = node_id
            self.is_test_mode = True
        self.skale = skale

        check_if_node_is_registered(self.skale, self.id)

        node_info = call_retry(self.skale.nodes.get, self.id)
        self.notifier = Notifier(node_info['name'], self.id, socket.inet_ntoa(node_info['ip']))
        self.notifier.send('SLA agent started', icon=MsgIcon.INFO)

        self.logger.info(f'Initialization of {self.agent_name} is completed. Node ID = {self.id}')

        self.nodes = []
        self.reward_period = call_retry.call(self.skale.constants_holder.get_reward_period)

    def get_last_reward_date(self):
        node_info = call_retry(self.skale.nodes.get, self.id)
        return node_info['last_reward_date']

    def generate_monitored_array(self):
        active_ids = self.skale.nodes.get_active_node_ids()
        active_ids.remove(self.id)

        if len(active_ids) <= MONITORED_NODES_COUNT:
            monitored_ids = active_ids
        else:
            monitored_ids = random.sample(active_ids, MONITORED_NODES_COUNT)
        monitored_nodes = []
        for id in monitored_ids:
            node_info = call_retry(self.skale.nodes.get, id)
            ip = socket.inet_ntoa(node_info['ip'])
            monitored_nodes.append({'id': id, 'ip': ip})
        return monitored_nodes

    def save_monitored_array(self, monitored_nodes):
        with open(MONITORED_NODES_FILEPATH, 'w') as json_file:
            json.dump({'last_reward_date': self.get_last_reward_date(),
                       'nodes': monitored_nodes}, json_file)

    def get_monitored_array(self):
        try:
            with open(MONITORED_NODES_FILEPATH) as json_file:
                data = json.load(json_file)
            if self.get_last_reward_date() > data['last_reward_date']:
                monitored_array = self.generate_monitored_array()
                self.save_monitored_array(monitored_array)
            else:
                monitored_array = data['nodes']
            return monitored_array

        except FileNotFoundError:
            self.logger.info('No json file with monitored nodes found. Creating a new one')
            monitored_array = self.generate_monitored_array()
            self.save_monitored_array(monitored_array)
            return monitored_array

    def validate_nodes(self, skale, nodes):
        """Validate nodes and returns a list of nodes to be reported."""
        self.logger.info(LONG_LINE)
        if len(nodes) == 0:
            self.logger.info('No nodes for monitoring')
        else:
            self.logger.info(f'Number of nodes for monitoring: {len(nodes)}')
            self.logger.info(f'Nodes for monitoring : {nodes}')

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(nodes)),
                                                   thread_name_prefix='MonThread') as executor:
            futures_for_node = {
                executor.submit(
                    get_metrics_for_node,
                    skale, node,
                    self.is_test_mode
                ): node
                for node in nodes
            }

            for future in futures_for_node:
                try:
                    metrics = future.result(timeout=55)
                except Exception as err:
                    self.logger.exception(f'Cannot get metrics for Node id = '
                                          f'{futures_for_node[future]["id"]}: {err}')
                else:
                    try:
                        db.save_metrics_to_db(self.id, futures_for_node[future]['id'],
                                              metrics['is_offline'], metrics['latency'])
                    except Exception as err:
                        self.notifier.send(f'Cannot save metrics to database - '
                                           f'is MySQL container running? {err}', icon=MsgIcon.ERROR)

    def get_reported_nodes(self, skale, nodes) -> list:
        """Returns a list of nodes to be reported."""
        last_block_number = skale.web3.eth.blockNumber
        block_data = call_retry.call(skale.web3.eth.getBlock, last_block_number)
        block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
        self.logger.info(f'Timestamp of current block: {block_timestamp}')

        nodes_for_report = []
        for node in nodes:
            # Check report date of current validated node
            rep_date = datetime.utcfromtimestamp(node['rep_date'])
            self.logger.info(f'Report date for node id={node["id"]}: {rep_date}')
            if rep_date < block_timestamp:
                # Forming a list of nodes that already have to be reported on
                nodes_for_report.append({'id': node['id'], 'rep_date': node['rep_date']})
        return nodes_for_report

    def send_reports(self, skale, nodes_for_report):
        """Send reports for every node from nodes_for_report."""
        self.logger.info(LONG_LINE)
        err_status = 0
        verdicts = []
        for node in nodes_for_report:
            start_date = node['rep_date'] - self.reward_period
            self.logger.info(f'Getting month metrics for node id = {node["id"]}:')
            self.logger.info(f'Query start date: {datetime.utcfromtimestamp(start_date)}')
            self.logger.info(f'Query end date: {datetime.utcfromtimestamp(node["rep_date"])}')
            try:

                metrics = db.get_month_metrics_for_node(self.id, node['id'],
                                                        datetime.utcfromtimestamp(start_date),
                                                        datetime.utcfromtimestamp(node['rep_date']))
            except Exception as err:
                self.notifier.send(f'Failed to get month metrics from db for node id = '
                                   f'{node["id"]}: {err}', icon=MsgIcon.ERROR)
            else:
                self.logger.info(f'Epoch metrics for node id = {node["id"]}: {metrics}')
                verdict = (node['id'], metrics['downtime'], metrics['latency'])
                verdicts.append(verdict)

        if len(verdicts) != 0:
            try:
                tx_res = skale.manager.send_verdicts(self.id, verdicts)
            except TransactionError as err:
                self.notifier.send(str(err), icon=MsgIcon.CRITICAL)
                raise

            self.logger.info('The report was successfully sent')
            self.logger.info(f'Tx hash: {tx_res.receipt}')
        return err_status

    def monitor_job(self) -> None:
        """
        Periodic job for monitoring nodes.
        """
        try:
            self.logger.info('New monitor job started...')
            skale = spawn_skale_lib(self.skale)

            if DISABLE_REPORTING:
                self.nodes = self.get_monitored_array()
            else:
                try:
                    self.nodes = call_retry.call(skale.monitors.get_checked_array, self.id)
                except Exception as err:
                    self.notifier.send(f'Failed to get list of monitored nodes. Error: {err}',
                                       icon=MsgIcon.ERROR)
                    self.logger.info('Monitoring nodes from previous job list')

            self.validate_nodes(skale, self.nodes)

            self.logger.info(f'{threading.enumerate()}')
            self.logger.info('Monitor job finished.')

        except Exception as err:
            self.notifier.send(f'Error occurred during monitoring job: {err}', icon=MsgIcon.ERROR)
            self.logger.exception(err)

    def report_job(self) -> bool:
        """
        Periodic job for sending reports.
        """
        try:
            self.logger.info('New report job started...')
            self.logger.info(f'{threading.enumerate()}')
            skale = spawn_skale_lib(self.skale)

            self.nodes = call_retry.call(skale.monitors.get_checked_array, self.id)
            nodes_for_report = self.get_reported_nodes(skale, self.nodes)

            if len(nodes_for_report) > 0:
                self.logger.info(f'Nodes for report ({len(nodes_for_report)}): {nodes_for_report}')
                check_required_balance(self.skale, self.notifier)
                self.send_reports(skale, nodes_for_report)
            else:
                self.logger.info('No nodes to be reported on')

            self.logger.info('Report job finished.')
        except Exception as err:
            self.notifier.send(f'Error occurred during report job: {err}', icon=MsgIcon.ERROR)
            self.logger.exception(err)
            return False
        else:
            return True

    def run(self) -> None:
        """Starts sla agent."""
        monitor_w = Worker()
        monitor_schedule = schedule.every(MONITOR_PERIOD).minutes.do(
            monitor_w.jobqueue.put, self.monitor_job)
        threading.Thread(target=monitor_w.worker, name='Monitor').start()
        monitor_schedule.run()

        # TODO: enable when move to validator-based monitoring
        if not DISABLE_REPORTING:
            reporter_w = Worker()
            report_schedule = schedule.every(REPORT_PERIOD).minutes.do(
                reporter_w.jobqueue.put, self.report_job)
            threading.Thread(target=reporter_w.worker, name='Reporter').start()
            report_schedule.run()

        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    skale = init_skale()
    monitor = Monitor(skale)
    monitor.run()
