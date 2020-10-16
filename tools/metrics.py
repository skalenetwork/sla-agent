#   -*- coding: utf-8 -*-
#
#   This file is part of sla-agent
#
#   Copyright (C) 2020-Present SKALE Labs
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

import pingparsing
import requests
from skale.dataclasses.skaled_ports import SkaledPorts
from skale.schain_config.ports_allocation import get_schain_base_port_on_node
from web3 import HTTPProvider, Web3

from configs import GOOD_IP, WATCHDOG_PORT, WATCHDOG_TIMEOUT, WATCHDOG_URL
from tools.exceptions import NoInternetConnectionException

logger = logging.getLogger(__name__)


def check_internet_connection():
    return not get_ping_node_results(GOOD_IP)['is_offline']


def get_metrics_for_node(skale, node, is_test_mode):
    if not check_internet_connection():
        raise NoInternetConnectionException
    host = GOOD_IP if is_test_mode else node['ip']

    metrics = get_ping_node_results(host)
    if not is_test_mode:
        healthcheck = get_containers_healthcheck(host)
        schains_check = check_schains_for_node(skale, node['id'], host)
        # schains_check = 0  # TODO Remove!!!
        metrics['is_offline'] = metrics['is_offline'] | healthcheck | schains_check

    logger.info(f'Received metrics from node ID = {node["id"]}: {metrics}')
    return metrics


def get_schain_endpoint(node_ip, rpc_port):
    return 'http://' + node_ip + ':' + str(rpc_port)


def check_schain(schain, node_ip):
    schain_name = schain['name']
    schain_endpoint = get_schain_endpoint(node_ip, schain['http_rpc_port'])
    logger.info(f'Checking s-chain {schain_name}: {schain_endpoint}')

    try:
        web3 = Web3(HTTPProvider(schain_endpoint, request_kwargs={'timeout': 10}))
        block_number = web3.eth.blockNumber
        logger.info(f"Current block number for {schain_name} = {block_number}")
        return 0
    except Exception as err:
        logger.error(f'Error occurred while getting block number: {err}')
        return 1


def check_schains_for_node(skale, node_id, node_ip):
    raw_schains = skale.schains.get_active_schains_for_node(node_id)

    node_info = skale.nodes.get(node_id)
    node_base_port = node_info['port']

    schains = [{'name': schain['name'],
                'index': schain['index'],
                'http_rpc_port':
                    get_schain_base_port_on_node(raw_schains, schain['name'],
                                                 node_base_port) + SkaledPorts.HTTP_JSON.value}
               for schain in raw_schains]
    logger.debug(f'schains = {schains}')
    for schain in schains:
        if check_schain(schain, node_ip) == 1:
            return 1

    return 0


def get_containers_healthcheck_url(host):
    return f'http://{host}:{WATCHDOG_PORT}/{WATCHDOG_URL}'


def get_containers_healthcheck(host):
    """Return 0 if OK or 1 if failed."""
    url = get_containers_healthcheck_url(host)
    try:
        response = requests.get(url, timeout=WATCHDOG_TIMEOUT)
    except requests.exceptions.ConnectionError as err:
        logger.info(f'Could not connect to {url}')
        logger.error(err)
        return 1
    except Exception as err:
        logger.info(f'Could not get data from {url}')
        logger.error(err)
        return 1

    if response.status_code != requests.codes.ok:
        logger.info(f'Request to {url} failed, status code: {response.status_code}')
        return 1

    res = response.json()
    if res.get('error') is not None:
        logger.info(res['error'])
        return 1
    data = res.get('data')
    if data is None:
        logger.info(f'No data found checking {url}')
        return 1

    for container in data:
        if not is_container_ok(container, host):
            return 1
    return 0


def is_container_ok(container, host):
    cont_status = True
    if not container['state']['Running']:
        logger.info(f'{container["name"]} is not running ({host})')
        cont_status = False
    if container['state']['Paused']:
        logger.info(f'{container["name"]} is paused ({host})')
        cont_status = False
    if (container['name'] == 'skale_admin' and
            container['state']['Health']['Status'] == 'unhealthy'):
        logger.info(f'{container["name"]} is not healthy ({host})')
        cont_status = False
    return cont_status


def get_ping_node_results(host) -> dict:
    """Returns a node host metrics (downtime and latency)."""
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination_host = host
    transmitter.ping_option = '-W1 -i 0.2'
    transmitter.count = 3
    result = transmitter.ping()
    logger.debug(f'Ping {host} results: {result}')
    if ping_parser.parse(
            result).as_dict()['rtt_avg'] is None or ping_parser.parse(
                result).as_dict()['packet_loss_count'] > 1:
        is_offline = True
        latency = -1
        logger.info(f'No ping response from host {host}')
    else:
        is_offline = False
        latency = int((ping_parser.parse(result).as_dict()['rtt_avg']) * 1000)

    return {'is_offline': is_offline, 'latency': latency}
