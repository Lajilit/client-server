# Реализовать метакласс ClientVerifier, выполняющий базовую проверку класса «Клиент»
# (для некоторых проверок уместно использовать модуль dis):
# отсутствие вызовов accept и listen для сокетов;
# использование сокетов для работы по TCP;
# отсутствие создания сокетов на уровне классов.
import dis
from socket import socket


class SocketVerifier(type):
    def __init__(cls, classname, bases, class_dict):
        cls.verify_socket(classname, class_dict)
        type.__init__(cls, classname, bases, class_dict)

    @staticmethod
    def verify_socket(classname, class_dict):
        socket_store = None
        for key, value in class_dict.items():
            assert not isinstance(value, socket), 'Не происходит создание сокета на уровне класса'
            if key == 'set_up':
                instructions = dis.get_instructions(value)
                for inst in instructions:
                    if inst.argval == 'socket' and inst.opname == 'LOAD_GLOBAL':
                        while inst.opname != 'STORE_ATTR':
                            inst = next(instructions)
                            if inst.opname == 'LOAD_GLOBAL' and inst.arg == 2:
                                assert inst.argval == 'SOCK_STREAM', 'доступно соединение только по TCP'
                        socket_store = inst.argval

        for key, value in class_dict.items():
            if key == 'set_up':
                if socket_store:
                    forbidden_methods = ['listen', 'accept'] if classname == 'Client' else ['connect']
                    instructions = dis.get_instructions(value)
                    for inst in instructions:
                        if inst.argval == socket_store:
                            next_inst = next(instructions)
                            assert not (next_inst.argval in forbidden_methods and
                                        next_inst.opname == 'LOAD_METHOD'), \
                                f'{classname} не должен иметь метод {next_inst.argval}'
