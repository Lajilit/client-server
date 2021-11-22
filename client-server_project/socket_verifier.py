import dis
from socket import socket

from socket_include import SocketType


class SocketVerifier(type):
    def __init__(cls, classname, bases, class_dict):
        cls.verify_socket(classname, class_dict)
        type.__init__(cls, classname, bases, class_dict)

    @staticmethod
    def verify_socket(classname, class_dict):
        socket_type = class_dict.get('socket_type')
        desired_argval = 'socket'
        checked_operation = 'LOAD_GLOBAL'
        checked_argument_number = 2
        operation_to_stop = 'STORE_ATTR'

        argval_for_TCP = 'SOCK_STREAM'
        forbidden_methods = []
        if socket_type == SocketType.CLIENT:
            forbidden_methods = ['listen', 'accept']
        elif socket_type == SocketType.SERVER:
            forbidden_methods = ['connect']

        forbidden_methods_opname = 'LOAD_METHOD'

        for key, value in class_dict.items():
            assert not isinstance(value, socket), 'Сокет не должен создаваться на уровне класса'
            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for inst in instructions:
                    if inst.argval == desired_argval and inst.opname == checked_operation:
                        while inst.opname != operation_to_stop:
                            inst = next(instructions)
                            if inst.opname == checked_operation and inst.arg == checked_argument_number:
                                assert inst.argval == argval_for_TCP, 'Доступно соединение только по TCP'

        for key, value in class_dict.items():
            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for inst in instructions:
                    if inst.argval == desired_argval:
                        next_inst = next(instructions)
                        assert not (next_inst.argval in forbidden_methods and
                                    next_inst.opname == forbidden_methods_opname), \
                            f'{classname} не должен использовать метод {next_inst.argval}'
