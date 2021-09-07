"""3. Задание на закрепление знаний по модулю yaml.
Написать скрипт, автоматизирующий сохранение данных в файле
YAML-формата. Для этого:
Подготовить данные для записи в виде словаря, в котором первому ключу
соответствует список, второму — целое число, третьему — вложенный
словарь, где значение каждого ключа — это целое число с юникод-символом,
 отсутствующим в кодировке ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл
file.yaml. При этом обеспечить стилизацию файла с помощью параметра
default_flow_style, а также установить возможность работы с юникодом:
allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают
 ли они с исходными."""
import yaml


def write_to_yaml(data):
    with open('data_yaml.yaml', 'w') as yaml_write_file:
        yaml.dump(data, yaml_write_file, allow_unicode=True,
                  default_flow_style=False, indent=4)


if __name__ == "__main__":
    data_to_yaml = {
        'list': [1, 2, 3, 4, 5],
        'number': 12345,
        'dict': {
            'key_1': '1\u00A3',
            'key_2': '2\u00A5',
            'key_3': '3\u00A7',
        }
    }
    write_to_yaml(data_to_yaml)
    with open('data_yaml.yaml') as yaml_read_file:
        data_from_yaml = yaml.load(yaml_read_file, Loader=yaml.FullLoader)
    print(data_from_yaml)
    print(data_from_yaml == data_to_yaml)
