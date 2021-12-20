import dis
from socket import socket

from socket_include import SocketType


class SocketVerifier(type):
    def __init__(cls, classname, bases, class_dict):
        cls.verify_socket(classname, class_dict)
        type.__init__(cls, classname, bases, class_dict)

    @staticmethod
    def verify_socket(classname, class_dict):
        # определяем, сервер или клиент
        socket_type = class_dict.get('socket_type')
        # ищем все инструкции для socket
        desired_argval = 'socket'
        # ищем все инструкции, где происходит загрузка глобальных имен
        checked_operation = 'LOAD_GLOBAL'
        # порядковый номер номер аргумента SOCK_STREAM - просто дикий хардкод!!!
        checked_argument_number = 2
        # условие для остановки перебора инструкций
        instructions_to_stop = 'CALL_METHOD', 'CALL_FUNCTION'
        # ищем значение для TCP
        argval_for_TCP = 'SOCK_STREAM'

        # в зависимости от того, сервер это или клиент, некоторе методы использовать нельзя
        forbidden_methods_opname = 'LOAD_METHOD'
        forbidden_methods = []
        if socket_type == SocketType.CLIENT:
            forbidden_methods = ['listen', 'accept']
        elif socket_type == SocketType.SERVER:
            forbidden_methods = ['connect']

        # перебираем все аргументы и методы класса
        for key, value in class_dict.items():
            # проверяем, что не создается сокетов на уровне класса
            assert not isinstance(value, socket), 'Сокет не должен создаваться на уровне класса'
            try:
                # для каждого метода дизасемблируем инструкции
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for inst in instructions:
                    # для каждой инструкии проверяем, связана ли она с socket
                    if inst.argval == desired_argval and inst.opname == checked_operation:
                        # если инструкция связана с использованием глобального имени socket,
                        # проверяем следующие инструкции
                        next_inst = inst
                        # пока не остановимся на вызове метода или функции, иначе мы не остановимся никогда
                        while next_inst.opname not in instructions_to_stop:
                            try:
                                next_inst = next(instructions)
                            except StopIteration:
                                break
                            # ищем инструкцию, где фигурирует аргумент с глобальным именем и порядковым номером 2
                            if next_inst.opname == checked_operation and next_inst.arg == checked_argument_number:
                                # проверяем, что это имя - SOCK_STREAM
                                assert next_inst.argval == argval_for_TCP, 'Доступно соединение только по TCP'
                    # также проверяем инструкции, где socket - не глобальное имя, а имя метода или атрибута
                    elif inst.argval == desired_argval:
                        # и если найдем, проверяем следующую инструкцию
                        next_inst = next(instructions)
                        # - в ней не должны использоваться запрещенные методы
                        assert not (next_inst.argval in forbidden_methods and
                                    next_inst.opname == forbidden_methods_opname), \
                            f'{classname} не должен использовать метод {next_inst.argval}'
