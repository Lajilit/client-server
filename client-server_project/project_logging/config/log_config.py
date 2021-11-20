import os, sys

parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(parent_directory)

import logging, logging.handlers

logs_formatter = logging.Formatter(
    '%(asctime)-25s %(levelname)-10s %(filename)s    %(message)s'
)

logs_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(logs_formatter)
console_handler.setLevel(logging.INFO)

client_logs_file = os.path.join(logs_file, 'logs', 'client.log')
client_file_handler = logging.FileHandler(client_logs_file, encoding='UTF-8')
client_file_handler.setFormatter(logs_formatter)
client_file_handler.setLevel(logging.DEBUG)

client_logger = logging.getLogger('client')
client_logger.addHandler(console_handler)
client_logger.addHandler(client_file_handler)
client_logger.setLevel(logging.DEBUG)


server_logs_file = os.path.join(logs_file, 'logs', 'server.log')
server_file_handler = logging.handlers.TimedRotatingFileHandler(
    server_logs_file, encoding='UTF-8', interval=1, when='midnight'
)
server_file_handler.setFormatter(logs_formatter)
server_file_handler.setLevel(logging.DEBUG)

server_logger = logging.getLogger('server')
server_logger.addHandler(console_handler)
server_logger.addHandler(server_file_handler)
server_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    server_logger.critical('critical')
    server_logger.error('error')
    server_logger.warning('warning')
    server_logger.info('info')
    server_logger.debug('debug')
    client_logger.critical('critical')
    client_logger.error('error')
    client_logger.warning('warning')
    client_logger.info('info')
    client_logger.debug('debug')
