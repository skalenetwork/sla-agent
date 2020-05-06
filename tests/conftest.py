""" SKALE config test """

import pytest
from skale import Skale
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

from tests.constants import ENDPOINT, ETH_PRIVATE_KEY, TEST_ABI_FILEPATH


@pytest.fixture
def skale():
    '''Returns a SKALE instance with provider from config'''
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet)
