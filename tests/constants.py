""" SKALE test constants """

import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

N_TEST_WALLETS = 2

ENDPOINT = os.environ['ENDPOINT']
TEST_ABI_FILEPATH = '/skale_vol/contracts_info/manager.json'
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']

# validator

D_VALIDATOR_ID = 1
D_VALIDATOR_NAME = 'test'
D_VALIDATOR_DESC = 'test'
D_VALIDATOR_FEE = 10
D_VALIDATOR_MIN_DEL = 1000

TEST_EPOCH = 40
TEST_DELTA = 10

N_TEST_NODES = 2

FAKE_IP = '10.1.0.1'
FAKE_REPORT_DATE = 1567690544
