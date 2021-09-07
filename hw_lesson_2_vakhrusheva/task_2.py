"""2. Задание на закрепление знаний по модулю json.
Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными. Для этого:
1) Создать функцию write_order_to_json(), в которую передается 5
параметров — товар (item), количество (quantity), цена (price),
покупатель (buyer), дата (date).
Функция должна предусматривать запись данных в виде словаря в файл
orders.json.
При записи данных указать величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json()
с передачей в нее значений каждого параметра."""
import json


def write_order_to_json(item, quantity, price, buyer, date):
    order_dict = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }
    with open('orders.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    data['orders'].append(order_dict)

    with open('orders.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == '__main__':
    write_order_to_json('chair', 2, 550.00, 'Екатерина', '26.08.2021')
    write_order_to_json('table', 1, 15000.00, 'Анатолий', '26.08.2021')
