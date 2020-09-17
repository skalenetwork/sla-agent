#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2019 SKALE Labs
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

import json

from configs import NODE_CONFIG_FILEPATH
from tools.helper import get_id_from_config


def test_get_id_from_config():
    node_index = 1

    with open(NODE_CONFIG_FILEPATH, 'w') as json_file:
        json.dump({'node_id': node_index}, json_file)

    node_id = get_id_from_config(NODE_CONFIG_FILEPATH)
    assert node_id == node_index
