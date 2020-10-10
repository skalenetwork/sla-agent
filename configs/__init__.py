import os

ENV = os.environ.get('ENV')

LONG_LINE = '-' * 100
LONG_DOUBLE_LINE = '=' * 100

NOTIFIER_URL = 'http://localhost:3007/send-tg-notification'
SKALE_VOLUME_PATH = '/skale_vol'
NODE_DATA_PATH = '/skale_node_data'

CONTRACTS_INFO_FOLDER_NAME = 'contracts_info'
MANAGER_CONTRACTS_INFO_NAME = 'manager.json'
CONTRACTS_INFO_FOLDER = os.path.join(SKALE_VOLUME_PATH, CONTRACTS_INFO_FOLDER_NAME)
NODE_CONFIG_FILENAME = 'node_config.json'
NODE_CONFIG_FILEPATH = os.path.join(NODE_DATA_PATH, NODE_CONFIG_FILENAME)

GOOD_IP = '127.0.0.1' if ENV == 'DEV' else '8.8.8.8'
MONITOR_PERIOD = 60
REPORT_PERIOD = 15

WATCHDOG_URL = 'status/core'
WATCHDOG_PORT = '3009'
