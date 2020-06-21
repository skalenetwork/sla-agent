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

import json
import logging
import os

import requests
import tenacity
from skale import Skale
from skale.wallets import RPCWallet

from configs import GAS_LIMIT, MIN_ETH_AMOUNT, NOTIFIER_URL
from configs.web3 import ABI_FILEPATH, ENDPOINT
from tools.exceptions import NodeNotFoundException, NotEnoughEthForTxException

logger = logging.getLogger(__name__)


call_retry = tenacity.Retrying(stop=tenacity.stop_after_attempt(10),
                               wait=tenacity.wait_fixed(2),
                               reraise=True)


def init_skale():
    return Skale(ENDPOINT, ABI_FILEPATH, RPCWallet(os.environ['TM_URL']))


def check_if_node_is_registered(skale, node_id):
    if node_id not in skale.nodes.get_active_node_ids():
        err_msg = f'There is no Node with ID = {node_id} in SKALE manager'
        logger.error(err_msg)
        raise NodeNotFoundException(err_msg)
    return True


def check_required_balance(skale):
    address = skale.wallet.address
    eth_bal_before_tx = skale.web3.eth.getBalance(address)
    if eth_bal_before_tx < MIN_ETH_AMOUNT:
        logger.info(f'ETH balance: {eth_bal_before_tx} is less than {MIN_ETH_AMOUNT}')
        # TODO: notify SKALE Admin
    min_eth_for_tx = GAS_LIMIT * skale.gas_price
    if eth_bal_before_tx < min_eth_for_tx:
        logger.info(f'ETH balance ({eth_bal_before_tx}) is too low, {min_eth_for_tx} required')
        # TODO: notify SKALE Admin
        raise NotEnoughEthForTxException(f'ETH balance is too low to send a transaction: '
                                         f'{eth_bal_before_tx}')


@tenacity.retry(
    wait=tenacity.wait_fixed(20),
    retry=tenacity.retry_if_exception_type(KeyError) | tenacity.retry_if_exception_type(
        FileNotFoundError))
def get_id_from_config(node_config_filepath) -> int:
    """Gets node ID from config file for agent initialization."""
    try:
        logger.debug('Reading node id from config file...')
        with open(node_config_filepath) as json_file:
            data = json.load(json_file)
        return data['node_id']
    except (FileNotFoundError, KeyError) as err:
        logger.warning(
            'Cannot read a node id from config file - is the node already registered?')
        raise err


class Notifier:
    def __init__(self, node_name, node_id, node_ip):
        self.header = f'Container: bounty-agent; Node: {node_name}, ' \
                      f'ID: {node_id}, IP: {node_ip}\n\n'

    def send(self, message, title=None):
        """Send message to telegram."""
        logger.info(message)

        if title is not None:
            header = title + '\n' + self.header
        else:
            header = self.header
        # if DEBUG:
        #     send_test(header + message)
        #     return 0

        message_data = {"message": header + message}

        try:
            response = requests.post(url=NOTIFIER_URL, json=message_data)
        except requests.exceptions.ConnectionError as err:
            logger.info(f'Could not connect to {NOTIFIER_URL}. {err}')
            return 1
        except Exception as err:
            logger.info(f'Cannot notify validator {NOTIFIER_URL}. {err}')
            return 1

        if response.status_code != requests.codes.ok:
            logger.info(f'Request to {NOTIFIER_URL} failed, status code: {response.status_code}')
            return 1

        res = response.json()
        if res.get('status') == 'error':
            logger.dubug(f"Cannot notify validator: {res['payload']}")
            logger.info('Telegram notifications are not supported on the node')
            return 1
        logger.debug('Message to validator was sent successfully')
        return 0
