import os, sys

parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(parent_directory)

import logging, logging.handlers

server_formatter = logging.Formatter(
    '%(asctime)-25s %(levelname)-10s %(filename)s    %(message)s'
)

server_logs_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server_logs_file = os.path.join(server_logs_file, 'logs', 'server.log')

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(server_formatter)
console_handler.setLevel(logging.INFO)

file_handler = logging.handlers.TimedRotatingFileHandler(
    server_logs_file, encoding='UTF-8', interval=1, when='midnight'
)
file_handler.setFormatter(server_formatter)
file_handler.setLevel(logging.DEBUG)

server_logger = logging.getLogger('server')
server_logger.addHandler(console_handler)
server_logger.addHandler(file_handler)
server_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    server_logger.critical('critical')
    server_logger.error('error')
    server_logger.warning('warning')
    server_logger.info('info')
    server_logger.debug('debug')
