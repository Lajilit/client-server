# Написать функцию host_range_ping() для перебора ip-адресов из заданного
# диапазона. Меняться должен только последний октет каждого адреса.
# По результатам проверки должно выводиться соответствующее сообщение.

import platform  # For getting the operating system name
import subprocess  # For executing a shell command
from ipaddress import ip_address


def host_range_ping(network, start, end):
    """
        Функция проверяет доступность ip-адресов из заданного диапазона и
        выводит ответ в виде строки «Узел доступен» или «Узел недоступен»
        network - ip-адрес сети,
        start - начальное значение последнего октета ip-адреса в диапазоне
        end - конечное значение последнего октета ip-адреса в диапазоне
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        network = ip_address(network)
    except ValueError:
        print(f'{network} Неверный ip-адрес сети')
    else:
        try:
            start = int(start)
            ens = int(end)
            if not 1 <= start <= 255 or not 1 <= end <= 255:
                raise ValueError
        except ValueError:
            print(f'({start} - {end}) - Неверное значение границ диапазона')
        else:
            start_ip = network + start
            end_ip = network + end
            while start_ip <= end_ip:
                command = ['ping', param, '1', str(start_ip)]
                result = 'Узел недоступен' if subprocess.call(
                    command) != 0 else 'Узел доступен'
                print(f'{start_ip} - {result}')
                start_ip += 1


if __name__ == '__main__':
    host_range_ping('192.168.1.0', 1, 3)
    host_range_ping('192.168.1.0', 1, -3)
    host_range_ping('192.168.1.0', 'f', 5)
    host_range_ping('192.168.1.0', '1', 5)
    host_range_ping('192.16d8.1.0', 1, 5)
    host_range_ping('192.1668.1.0', 1, 5)
    host_range_ping('192.168.1.0', 0, 5)