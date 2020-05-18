""" SKALE config test """

import pytest
from skale import Skale
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

from tests.constants import ENDPOINT, ETH_PRIVATE_KEY, N_TEST_NODES, TEST_ABI_FILEPATH
from tests.prepare_validator import create_dirs, create_set_of_nodes, get_active_ids


@pytest.fixture(scope="session")
def skale():
    """Returns a SKALE instance with provider from config"""
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet)

    create_dirs()
    ids = get_active_ids(skale)
    print(f'Existing Node IDs = {ids}')
    cur_node_id = max(ids) + 1 if len(ids) else 0
    create_set_of_nodes(skale, cur_node_id, N_TEST_NODES)
    return skale
