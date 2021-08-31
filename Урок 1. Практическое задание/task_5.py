"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess
import chardet

args = {
    'yandex': ['ping', 'yandex.ru'],
    'youtube': ['ping', 'youtube.com']
}

for k, v in args.items():
    ping = subprocess.Popen(args[k], stdout=subprocess.PIPE)
    for line in ping.stdout:
        # данные получаем в виде байт. так как текст написан латиницей,
        # он выводится корректно - чтобы убедиться можно раскомментировать:
        # print(line)
        # определяем исходную кодировку
        result = chardet.detect(line)
        # переводим в unicode, хотя у нас и нет кириллицы
        line = line.decode(result['encoding']).encode('utf-8')
        # переводим в строковый тип и выводим данные
        print(line.decode('utf-8'))
