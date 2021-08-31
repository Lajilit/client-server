Протокол обмена

За основу протокола обмена между клиентом и сервером взят проект JIM (JSON instant messaging)
Протокол JIM базируется на передаче JSON-объектов через TCP-сокеты.
Все сетевые взаимодействия осуществляются в байтах.
Спецификация объектов
JSON-данные, пересылаемые между клиентом и сервером, обязательно должны содержать поля action и time.
Поле action задает тип сообщения между клиентом и сервером. А time —временная метка отправки JSON-объекта, UNIX-время (число секунд от 1 января 1970 года).
Например, для аутентификации надо сформировать JSON-объект:
{
 "action": "authenticate",
 "time": <unix timestamp>,
        "user": {
                "account_name": "C0deMaver1ck",
                "password":     "CorrectHorseBatterStaple"
        }
}


Ответы сервера должны содержать поле response, и могут — поле alert/error с текстом ошибки.
{
    "response": <код ответа>,
    "alert": <текст ответа>
}

Все объекты имеют ограничения длины (количество символов):
поле action — 15 символов (сейчас самое длинное название — authenticate (11 символов); вряд ли должно понадобиться что-то больше);
поле response — с кодом ответа сервера, это 3 цифры;
имя пользователя / название чата (name): 25 символов;
сообщение — максимум 500 символов (" ").
Итоговое ограничение для JSON-объекта — 640 символов (можно добавить дополнительные поля или изменить имеющиеся). Исходные ограничения на длину сообщений упрощают реализации клиента и сервера.
Подключение, отключение, авторизация
JIM-протокол не подразумевает обязательной авторизации при подключении к серверу. Это позволяет реализовать функционал для гостевых пользователей.
Если какое-то действие требует авторизации, сервер должен ответить соответствующим кодом ошибки — 401.
После подключения при необходимости авторизации клиент должен отправить сообщение с логином/паролем, например:
{
        "action": "authenticate",
        "time": <unix timestamp>,
        "user": {
                "account_name":  "C0deMaver1ck",
                "password":      "CorrectHorseBatteryStaple"
        }
}


В ответ сервер может прислать один из кодов:
{
    "response": 200,
    "alert":"Необязательное сообщение/уведомление"
}

{
    "response": 402,
    "error": "This could be "wrong password" or "no account with that name""
}

{
    "response": 409,
    "error": "Someone is already connected with the given user name"
}


Отключение от сервера должно сопровождаться сообщением “quit”:
{
    "action": "quit"
}

Присутствие
Каждый пользователь при подключении к серверу отсылает сервисное сообщение о присутствии — presence с необязательным полем type:
{
        "action": "presence",
        "time": <unix timestamp>,
        "type": "status",
        "user": {
                "account_name":  "C0deMaver1ck",
                "status":      "Yep, I am here!"
        }
}


Чтобы проверить доступность пользователя online, сервер выполняет probe-запрос:
{
        "action": "probe",
        "time": <unix timestamp>,
}

Probe-запрос может отправлять только сервер, проверяя доступность клиентов из контакт-листа. На probe-запрос клиент должен ответить простым presence-сообщением.
Коды ответов сервера
JIM-протокол использует коды ошибок HTTP. Перечислим поддерживаемые:
1xx — информационные сообщения:
100 — базовое уведомление;
101 — важное уведомление.
2xx — успешное завершение:
200 — OK;
201 (created) — объект создан;
202 (accepted) — подтверждение.
4xx — ошибка на стороне клиента:
400 — неправильный запрос/JSON-объект;
401 — не авторизован;
402 — неправильный логин/пароль;
403 (forbidden) — пользователь заблокирован;
404 (not found) — пользователь/чат отсутствует на сервере;
409 (conflict) — уже имеется подключение с указанным логином;
410 (gone) — адресат существует, но недоступен (offline).
5xx — ошибка на стороне сервера:
500 — ошибка сервера.
Коды ошибок могут быть дополнены новыми.

Сообщения-ответы имеют следующий формат (в зависимости от кода ответа):
{
    "response": 1xx / 2xx,
    "time": <unix timestamp>,
    "alert": "message (optional for 2xx codes)"
}


Или такой:
{
    "response": 4xx / 5xx,
    "time": <unix timestamp>,
    "error": "error message (optional)"
}

Сообщение «Пользователь–Пользователь»
Простое сообщение имеет формат:
{
    "action": "msg",
    "time": <unix timestamp>,
    "to": "account_name",
    "from": "account_name",
    "encoding": "ascii",
    "message": "message"
}

Когда сервер видит действие msg, ему не нужно читать или парсить все сообщение — только проверить адресата и передать месседж ему.
Если поле to (адресат) имеет префикс # — это сообщение для группы. Обрабатывается, как приватное сообщение, но по шаблону «Пользователь-Чат»
В ответ на такое событие клиенту возвращается код ошибки.
Поле encoding указывает кодировку сообщения. Если нет, считается ascii.
Сообщение «Пользователь-Чат».
Обрабатывается, как и «Пользователь-Пользователь», но с дополнением:
Имя чата имеет префикс # (то есть сервер должен проверять поле to для всех сообщений и переправлять месседж всем online-пользователям данного чата).

Сообщение:
{
    "action": "msg",
    "time": <unix timestamp>,
    "to": "#room_name",
    "from": "account_name",
    "message": "Hello World"
}


Присоединиться к чату:
{
    "action": "join",
    "time": <unix timestamp>,
    "room": "#room_name"
}


Покинуть чат:
{
    "action": "leave",
    "time": <unix timestamp>,
    "room": "#room_name"
}

Методы протокола (actions)
“action”: “presence” — присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online;
“action”: “prоbe” — проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online;
“action”: “msg” — простое сообщение пользователю или в чат;
“action”: “quit” — отключение от сервера;
“action”: “authenticate” — авторизация на сервере;
“action”: “join” — присоединиться к чату;
“action”: “leave” — покинуть чат.
Протокол может быть расширен новыми методами.
