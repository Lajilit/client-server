"""
Задание 2.

Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя!!! методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.
"""

words = [b'class', b'function', b'method']

for i in range(len(words)):
    word = words[i]
    print(f'Слово № {i+1}')
    print(f'    Содержимое: {word}')
    print(f'    Тип: {type(word)}')
    print(f'    Длина: {len(word)}')

