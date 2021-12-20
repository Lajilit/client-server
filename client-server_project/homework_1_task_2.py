"""Написать функцию host_range_ping() для перебора ip-адресов из заданного
диапазона. Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
from homework_1_task_1 import ping_host

from ipaddress import ip_address


def check_ip(ip):
    try:
        ip = ip_address(ip)
    except ValueError:
        print(f'{ip} Неверный начальный ip-адрес')
    else:
        return ip


def check_count(count):
    try:
        count = int(count)
        if not 1 <= count <= 255:
            raise ValueError
    except ValueError:
        print(f'{count} - Неверное значение количества проверяемых адресов')
    else:
        return count


def check_ip_range(start_ip, ip_count):
    max_count = 256 - int(start_ip.split('.')[-1])
    start_ip = check_ip(start_ip)
    ip_count = check_count(ip_count)
    if start_ip and ip_count:
        if max_count < ip_count:
            print(f'Некоторые IP-адреса выходят за границы заданного диапазона, '
                  f'будут проверены только {max_count} IP-адресов')
            ip_count = max_count
        end_ip = start_ip + ip_count - 1
        print(f'Проверка доступности ip-адресов от {start_ip} до {end_ip}')
        return start_ip, end_ip


def host_range_ping(start_ip, ip_count):
    try:
        start, end = check_ip_range(start_ip, ip_count)
    except TypeError:
        pass
    else:
        while start <= end:
            print(f'{start} - {ping_host(str(start))}')
            start += 1


if __name__ == '__main__':
    host_range_ping('192.168.1.255', 2)
    host_range_ping('192.168.1.0', -3)
    host_range_ping('192.168.1.0', 256)
    host_range_ping('192.168.1.0', 'f')
    host_range_ping('192.168.1.0', '1')
    host_range_ping('192.16d8.1.0', 2)
    host_range_ping('192.1668.1.0', 2)
    host_range_ping('192.168.1.0', 0)
    host_range_ping('192.168.1.0', 20)
