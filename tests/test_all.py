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
from tests.constants import FAKE_IP, FAKE_REPORT_DATE, N_TEST_NODES
from tests.prepare_validator import (
    TEST_DELTA, TEST_EPOCH, create_dirs, create_set_of_nodes,
    get_active_ids)
from tools import db
from configs import LONG_LINE
from tools.helper import check_if_node_is_registered, init_skale

skale = init_skale()


def setup_module(module):
    create_dirs()
    global cur_node_id
    global nodes_count_before, nodes_count_to_add
    ids = get_active_ids(skale)
    print(f'ids = {ids}')
    nodes_count_before = len(ids)
    cur_node_id = max(ids) + 1 if nodes_count_before else 0
    nodes_count_to_add = N_TEST_NODES
    create_set_of_nodes(skale, cur_node_id, nodes_count_to_add)
    print(f'Time just after nodes creation: {datetime.utcnow()}')


@pytest.fixture(scope="module")
def monitor(request):
    print(f'\nInit Monitor for_node ID = {cur_node_id}')
    _monitor = sla.Monitor(skale, cur_node_id)

    return _monitor


def test_nodes_are_created():

    nodes_count_after = len(get_active_ids(skale))
    print(f'\nwait nodes_number = {nodes_count_before + nodes_count_to_add}')
    print(f'got nodes_number = {nodes_count_after}')

    assert nodes_count_after == nodes_count_before + nodes_count_to_add


def test_check_if_node_is_registered():
    assert check_if_node_is_registered(skale, cur_node_id)
    assert check_if_node_is_registered(skale, cur_node_id + 1)
    assert not check_if_node_is_registered(skale, 100)


def test_monitor_job_saves_data(monitor):
    db.clear_all_reports()
    monitor.monitor_job()
    assert db.get_count_of_report_records() == 1


def test_send_reports_neg(monitor):
    skale = monitor.skale
    print(f'--- Gas Price = {monitor.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{monitor.skale.web3.eth.getBalance(monitor.skale.wallet.address)}')

    nodes = skale.monitors_data.get_checked_array(monitor.id)
    reported_nodes = monitor.get_reported_nodes(skale, nodes)
    assert type(reported_nodes) is list
    print(f'\nrep nodes = {reported_nodes}')
    assert len(reported_nodes) == 0

    print(LONG_LINE)
    print(f'Report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'Now date: {datetime.utcnow()}')

    fake_nodes = [{'id': 100, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    with pytest.raises(ValueError):
        monitor.send_reports(skale, fake_nodes)


def test_get_reported_nodes_pos(monitor):
    skale = monitor.skale
    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    nodes = skale.monitors_data.get_checked_array(monitor.id)
    print(LONG_LINE)
    print(f'report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'now: {datetime.utcnow()}')
    reported_nodes = monitor.get_reported_nodes(skale, nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')

    assert any(node.get('id') == cur_node_id + 1 for node in reported_nodes)


def test_send_reports_pos(monitor):
    print(f'--- Gas Price = {skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{skale.web3.eth.getBalance(skale.wallet.address)}')

    reported_nodes = monitor.get_reported_nodes(skale, monitor.nodes)
    db.clear_all_reports()
    assert monitor.send_reports(skale, reported_nodes) == 0


def test_report_job_saves_data(monitor):
    db.clear_all_report_events()
    print(f'Sleep for {TEST_DELTA} sec')
    time.sleep(TEST_DELTA)
    tx_res = skale.manager.get_bounty(cur_node_id + 1, wait_for=True)
    tx_res.raise_for_status()
    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    monitor.report_job()
    assert db.get_count_of_report_events_records() == 1
