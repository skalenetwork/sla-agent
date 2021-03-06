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

from unittest import mock

import requests

from configs import WATCHDOG_PORT, WATCHDOG_URL
from tools.metrics import get_containers_healthcheck


def get_test_url(base):
    return f'http://{base}:{WATCHDOG_PORT}/{WATCHDOG_URL}'


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    data_ok1 = [{'name': 'container_name', 'state': {'Running': True, 'Paused': False}}]
    data_bad1 = [{'name': 'container_name', 'state': {'Running': False, 'Paused': False}}]
    data_bad2 = [{'name': 'container_name', 'state': {'Running': False, 'Paused': True}}]

    if args[0] == get_test_url('url_ok1'):
        return MockResponse({'error': None, 'data': data_ok1}, 200)
    elif args[0] == get_test_url('url_bad1'):
        return MockResponse({'error': None, 'data': data_bad1}, 200)
    elif args[0] == get_test_url('url_bad2'):
        return MockResponse({'error': 'any_error', 'data': data_ok1}, 200)
    elif args[0] == get_test_url('url_bad3'):
        return MockResponse({'error': None, 'data': data_ok1}, 500)
    elif args[0] == get_test_url('url_bad4'):
        return MockResponse({'error': None, 'data': data_bad2}, 200)
    elif args[0] == get_test_url('url_bad5'):
        return MockResponse({'error': None}, 200)

    return MockResponse(None, 404)


def connection_error(*args, **kwargs):
    raise requests.exceptions.ConnectionError


def unknown_error(*args, **kwargs):
    raise Exception


@mock.patch('tools.metrics.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_pos(mock_get):
    res = get_containers_healthcheck('url_ok1')
    assert res == 0


@mock.patch('tools.metrics.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_neg(mock_get):
    res = get_containers_healthcheck('url_bad1')
    assert res == 1
    res = get_containers_healthcheck('url_bad2')
    assert res == 1
    res = get_containers_healthcheck('url_bad3')
    assert res == 1
    res = get_containers_healthcheck('url_bad4')
    assert res == 1
    res = get_containers_healthcheck('url_bad5')
    assert res == 1
    res = get_containers_healthcheck('url_bad6')
    assert res == 1


@mock.patch('tools.metrics.requests.get', side_effect=connection_error)
def test_healthcheck_connection_error(mock_get):
    res = get_containers_healthcheck('url_ok')
    assert res == 1


@mock.patch('tools.metrics.requests.get', side_effect=unknown_error)
def test_healthcheck_unknown_error(mock_get):
    res = get_containers_healthcheck('url_ok')
    assert res == 1
