#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2019-2020 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
from datetime import datetime

import pytest
import sla_agent as sla
from configs import LONG_LINE
from skale.transactions.result import TransactionError
from tests.constants import FAKE_IP, FAKE_REPORT_DATE
from tests.prepare_validator import TEST_DELTA, TEST_EPOCH, get_active_ids
from tools import db
from tools.exceptions import NodeNotFoundException
from tools.helper import check_if_node_is_registered


@pytest.fixture(scope="module")
def cur_node_id(skale):
    ids = get_active_ids(skale)
    return len(ids) - 2


@pytest.fixture(scope="module")
def monitor(skale, cur_node_id):
    return sla.Monitor(skale, cur_node_id)


def test_check_if_node_is_registered(skale, cur_node_id):
    assert check_if_node_is_registered(skale, cur_node_id)
    assert check_if_node_is_registered(skale, cur_node_id + 1)
    with pytest.raises(NodeNotFoundException):
        check_if_node_is_registered(skale, 100)


def test_monitor_job_saves_data(monitor):
    db.clear_all_reports()
    monitor.monitor_job()
    assert db.get_count_of_report_records() == 1


@pytest.mark.skip(reason="temporary skip because of SKALE manager changes")
def test_send_reports_neg(skale, monitor):
    print(f'--- Gas Price = {monitor.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{monitor.skale.web3.eth.getBalance(monitor.skale.wallet.address)}')

    nodes = skale.monitors.get_checked_array(monitor.id)
    reported_nodes = monitor.get_reported_nodes(skale, nodes)
    assert type(reported_nodes) is list
    print(f'\nrep nodes = {reported_nodes}')
    assert len(reported_nodes) == 0

    print(LONG_LINE)
    print(f'Report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'Now date: {datetime.utcnow()}')

    fake_nodes = [{'id': 100, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    with pytest.raises(TransactionError):
        monitor.send_reports(skale, fake_nodes)


@pytest.mark.skip(reason="temporary skip because of SKALE manager changes")
def test_get_reported_nodes_pos(skale, monitor, cur_node_id):
    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    nodes = skale.monitors.get_checked_array(monitor.id)
    print(LONG_LINE)
    print(f'report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'now: {datetime.utcnow()}')
    reported_nodes = monitor.get_reported_nodes(skale, nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')

    assert any(node.get('id') == cur_node_id + 1 for node in reported_nodes)


def test_send_reports_pos(skale, monitor):
    print(f'--- Gas Price = {skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{skale.web3.eth.getBalance(skale.wallet.address)}')
    nodes = skale.monitors.get_checked_array(monitor.id)
    reported_nodes = monitor.get_reported_nodes(skale, nodes)
    db.clear_all_reports()
    assert monitor.send_reports(skale, reported_nodes) == 0


@pytest.mark.skip(reason="temporary skip because of SKALE manager changes")
def test_report_job_saves_data(skale, monitor, cur_node_id):
    print(f'Sleep for {TEST_DELTA} sec')
    time.sleep(TEST_DELTA)
    tx_res = skale.manager.get_bounty(cur_node_id + 1, wait_for=True)
    tx_res.raise_for_status()
    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    assert monitor.report_job()
