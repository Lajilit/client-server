"""Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов. Аргументом функции является список,
котором каждый сетевой узел должен быть представлен именем хоста или
ip-адресом. В функции необходимо перебирать ip-адреса и проверять их
доступность с выводом соответствующего сообщения («Узел доступен»,
«Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться
с помощью функции ip_address()."""

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


def ping_host(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '1', host]
    reply = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    code = reply.wait()
    return 'Узел доступен' if code == 0 else 'Узел недоступен'


def ping_hosts(hosts_list):
    for host in hosts_list:
        print(f'{host} - {ping_host(host)}')


if __name__ == '__main__':
    hosts = ['192.569.1.1', '127.0.0.1', '8.8.8.8', '185.254.189.138', 'gb.ru', 'lajil.ru', '122.1.1.1']
    checked_hosts = []

    for host in hosts:
        if check_host(host):
            checked_hosts.append(host)
    ping_hosts(checked_hosts)
