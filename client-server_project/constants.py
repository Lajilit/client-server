# IP адрес и порт по умолчанию
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 7777
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длина сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'

# Протокол обмена: JIM
# Ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
TYPE = 'type'
ACCOUNT_NAME = 'account_name'
STATUS = 'status'
PRESENCE = 'presence'
RESPONSE = 'response'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
SENDER = 'to'
DESTINATION = 'from'
EXIT = 'exit'
ALERT = 'alert'
ERROR = 'error'
RESPONSE_200 = {
    RESPONSE: 200,
    ALERT: 'ok'
}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: 'Bad Request'
}