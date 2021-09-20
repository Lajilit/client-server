import os, sys

parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(parent_directory)

import logging

client_formatter = logging.Formatter(
    '%(asctime)-25s %(levelname)-10s %(filename)s    %(message)s'
)

client_logs_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client_logs_file = os.path.join(client_logs_file, 'logs', 'client.log')

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(client_formatter)
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler(client_logs_file, encoding='UTF-8')
file_handler.setFormatter(client_formatter)
file_handler.setLevel(logging.DEBUG)

client_logger = logging.getLogger('client')
client_logger.addHandler(console_handler)
client_logger.addHandler(file_handler)
client_logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    client_logger.critical('critical')
    client_logger.error('error')
    client_logger.warning('warning')
    client_logger.info('info')
    client_logger.debug('debug')

