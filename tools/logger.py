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

import logging
import logging.handlers as py_handlers
import os
import sys
from logging import Formatter, StreamHandler

from configs.logs import (LOG_BACKUP_COUNT, LOG_FILE_SIZE_BYTES, LOG_FOLDER,
                          LOG_FORMAT)


def init_logger(log_file_path):
    handlers = []

    formatter = Formatter(LOG_FORMAT)
    f_handler = py_handlers.RotatingFileHandler(log_file_path,
                                                maxBytes=LOG_FILE_SIZE_BYTES,
                                                backupCount=LOG_BACKUP_COUNT)

    f_handler.setFormatter(formatter)
    f_handler.setLevel(logging.INFO)
    handlers.append(f_handler)

    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)


def init_agent_logger(agent_name, node_id):
    log_path = get_log_filepath(agent_name, node_id)
    init_logger(log_path)


def get_log_filepath(file_name, node_id):
    if node_id is not None:
        file_name = f'{file_name}_{node_id}'
    log_filename = f'{file_name}.log'

    return os.path.join(LOG_FOLDER, log_filename)
