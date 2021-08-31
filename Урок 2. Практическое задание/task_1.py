"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt,
info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате
CSV. Для этого:
1) Создать функцию get_data(), в которой в цикле осуществляется перебор
файлов с данными, их открытие и считывание данных. В этой функции из
считанных данных необходимо с помощью регулярных выражений извлечь
значения параметров «Изготовитель системы», «Название ОС»,
«Код продукта», «Тип системы». Значения каждого параметра поместить в
соответствующий список. Должно получиться четыре списка — например,
os_prod_list, os_name_list, os_code_list, os_type_list.
2) В этой же функции создать главный список для хранения данных отчета —
 например, main_data — и поместить в него названия столбцов отчета в
 виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
 «Тип системы». Значения для этих столбцов также оформить в виде списка
 и поместить в файл main_data (также для каждого файла);
3) Создать функцию write_to_csv(), в которую передавать ссылку на
CSV-файл. В этой функции реализовать получение данных через вызов
функции get_data(), а также сохранение подготовленных данных в
соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""
import csv

from chardet import detect
import re


def decode_to_utf(file: str):
    with open(file, 'rb') as detect_file:
        text = detect_file.read()
        encoding = detect(text)['encoding']
        decode_text = bytes.decode(text, encoding=encoding).strip('\n').split(
            '\n')

    with open(file, 'w', encoding='utf-8') as decode_file:
        for line in decode_text:
            decode_file.write(line)


def get_data(files: list, params: list):
    main_data = [params, ]
    for file in files:
        list_data = []
        decode_to_utf(file)
        with open(file, 'r', encoding='utf-8') as data_file:
            data_lines = data_file.readlines()
        for param in params:
            for line in data_lines:
                if re.search(f'{param}:', line):
                    _, value = re.split(f'{param}:', line)
                    list_data.append(value.strip('\n').strip(' '))
        main_data.append(list_data)

    return main_data


def write_to_csv(csv_file, files: list, params: list):
    data = get_data(files, params)
    with open(csv_file, 'w', newline='') as write_file:
        csv_writer = csv.writer(write_file)
        csv_writer.writerows(data)


if __name__ == '__main__':
    files_list = [
        'info_1.txt',
        'info_2.txt',
        'info_3.txt'
    ]
    params_list = [
        'Изготовитель системы',
        'Название ОС',
        'Код продукта',
        'Тип системы'
    ]
    write_to_csv('file.csv', files_list, params_list)
    with open('file.csv') as read_file:
        print(read_file.read())
