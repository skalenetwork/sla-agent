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


from tools.helper import get_id_from_config
from tools.config_storage import ConfigStorage


def test_get_id_from_config():
    config_file_name = 'test_node_config'
    node_index = 1
    config_node = ConfigStorage(config_file_name)
    config_node.update({'node_id': node_index})
    node_id = get_id_from_config(config_file_name)
    assert node_id == node_index
