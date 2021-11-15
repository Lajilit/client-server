# Написать функцию host_ping(), в которой с помощью утилиты ping будет
# проверяться доступность сетевых узлов. Аргументом функции является список,
# котором каждый сетевой узел должен быть представлен именем хоста или
# ip-адресом. В функции необходимо перебирать ip-адреса и проверять их
# доступность с выводом соответствующего сообщения («Узел доступен»,
# «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться
# с помощью функции ip_address().

import platform  # For getting the operating system name
import socket
import subprocess  # For executing a shell command
from ipaddress import ip_address


def check_host(input_host):
    # проверка на то, получен ip-адрес или имя хоста
    is_ip = ''.join(input_host.split('.')).isdecimal()
    if is_ip:
        try:
            input_host = str(ip_address(input_host))
        except ValueError:
            print(f'{input_host} - неверный ip-адрес хоста')
        else:
            return True
    else:
        try:
            input_host = socket.gethostbyname_ex(input_host)
        except socket.gaierror:
            print(f'{input_host} - неверное имя хоста')
        else:
            return True


def host_ping(hosts_list):
    """
       Функция проверяет доступность сетевого узла из списка и выводит ответ
       в виде строки «Узел доступен» или «Узел недоступен»
       """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    for host in hosts_list:
        command = ['ping', param, '1', host]
        result = 'Узел недоступен' if subprocess.call(
            command) != 0 else 'Узел доступен'
        print(f'{host} - {result}')


if __name__ == '__main__':
    # hosts = [input('Введите ip-адрес или имя хоста: ') for i in range(5)]
    hosts = ['192.569.1.1', '127.0.0.1', '8.8.8.8', '185.254.189.138', 'gb.ru',
             'ghstf.ru']
    checked_hosts = []

    for host in hosts:
        if check_host(host):
            checked_hosts.append(host)
    host_ping(checked_hosts)
