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

import pytest

from configs import NODE_CONFIG_FILEPATH
from sla_agent import Monitor
from tools.config_storage import ConfigStorage
from tools.exceptions import NodeNotFoundException


def test_init_agent(skale):
    print("Test agent init with given node id")
    agent0 = Monitor(skale, 0)
    assert agent0.id == 0

    print("Test agent init without given node id - read id from file")
    config_node = ConfigStorage(NODE_CONFIG_FILEPATH)
    config_node.update({'node_id': 1})
    agent1 = Monitor(skale)
    assert agent1.id == 1

    print("Test agent init with non-existing node id")
    with pytest.raises(NodeNotFoundException):
        Monitor(skale, 100)

    print("Test agent init with non-integer node id")
    config_node.update({'node_id': 'one'})

    with pytest.raises(Exception):
        Monitor(skale)
