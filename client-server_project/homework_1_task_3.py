"""Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
(использовать модуль tabulate). """

from homework_1_task_1 import ping_host
from homework_1_task_2 import check_ip_range
from tabulate import tabulate


def host_range_ping_table(start_ip, ip_count):
    try:
        start, end = check_ip_range(start_ip, ip_count)
    except TypeError:
        pass
    else:
        ip_table = {}
        while start <= end:
            result = ping_host(str(start))
            ip = str(start)
            if result not in ip_table.keys():
                ip_table[result] = [ip]
            else:
                ip_table[result].append(ip)
            start += 1
        print(tabulate(ip_table, headers='keys'))


if __name__ == '__main__':
    host_range_ping_table('192.168.1.10', 10)
