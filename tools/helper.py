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

import tenacity
from skale import Skale
from skale.wallets import RPCWallet

from configs.web3 import ABI_FILEPATH, ENDPOINT
from tools.exceptions import NodeNotFoundException

logger = logging.getLogger(__name__)


call_retry = tenacity.Retrying(stop=tenacity.stop_after_attempt(10),
                               wait=tenacity.wait_fixed(2),
                               reraise=True)


def init_skale():
    return Skale(ENDPOINT, ABI_FILEPATH, RPCWallet(os.environ['TM_URL']))


def check_if_node_is_registered(skale, node_id):
    if node_id not in skale.nodes_data.get_active_node_ids():
        err_msg = f'There is no Node with ID = {node_id} in SKALE manager'
        logger.error(err_msg)
        raise NodeNotFoundException(err_msg)
    return True


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
        logger.warning('Cannot read a node id from config file - is the node already registered?')
        raise err
