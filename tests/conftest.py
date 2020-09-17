""" SKALE config test """

import pytest

from tests.constants import N_TEST_NODES
from tests.prepare_validator import (create_dirs, create_set_of_nodes,
                                     get_active_ids, init_skale_with_w3_wallet)


@pytest.fixture(scope="session")
def skale():
    """Returns a SKALE instance with provider from config"""
    skale = init_skale_with_w3_wallet()

    create_dirs()
    ids = get_active_ids(skale)
    print(f'Existing Node IDs = {ids}')
    cur_node_id = max(ids) + 1 if len(ids) else 0
    create_set_of_nodes(skale, cur_node_id, N_TEST_NODES)
    return skale
