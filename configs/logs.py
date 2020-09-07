import os

from configs import NODE_DATA_PATH

LOG_FOLDER_NAME = 'log'
LOG_FOLDER = os.path.join(NODE_DATA_PATH, LOG_FOLDER_NAME)

LOG_FILE_SIZE_MB = 100
LOG_FILE_SIZE_BYTES = LOG_FILE_SIZE_MB * 1000000

LOG_BACKUP_COUNT = 3

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(threadName)s]'
