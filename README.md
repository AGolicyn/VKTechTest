# Как этим пользоваться

Перейти в директорию с проектом, и выполнить команду:

```Bash
  docker compose up --build -d
```
```note
Я не создавал volume для базы данных, и она просто лежит внутри контейнера с начальными данными.
```
Можно перейти в работающий контейнер и выполнить ```python manage.py test```, чтобы запустить тесты и проверить корректность работы API.

## Пример использования сервиса друзей

Предположим у нас есть 4 друга: Саша, Маша, Юля, Вася

*Зарегистрируем их как пользователей*

Зарегистрируем Юлию с username=Julia, password=123 
    
```Bash     
    curl --request POST --location 'http://0.0.0.0:8000/registration/' \
    --form 'username="julia"' \
    --form 'password="123"'
```
Получим ответ: 
```Bash
    {"username":"julia"}
```
, значит пользователь успешно создан.

Так же создадим профили: 
Саша с username=sasha, password=345
Маша с username=masha, password=678
Вася с username=vasya, password=789


*Отправим от Маши запрос в друзья Саше и Юле*
    
Для этого обратимся к пути ```friend/<str:username>/request/```

Заметим, что у нас реализована BasicAuthentication, чтобы каждый мог взаимодействовать, только со своим аккаунтом

Для прохождения аутентификации в заголовки запроса добавим логин:пароль, которые закодируются в Base64
    
```Bash
    curl -u 'masha:678' --request POST --location 'http://0.0.0.0:8000/friend/sasha/request/'
    curl -u 'masha:678' --request POST --location 'http://0.0.0.0:8000/friend/julia/request/'
```

Получим ответ примерно такого формата: 
```Bash
  {"id":10,
    "from_user": {"username":"masha"},
    "to_user": {"username":"julia"},
    "created_at":"2023-05-09T19:55:18.374039Z"}
```

*Посмотрим от лица Маши список заявок в друзья*

Для этого обратимся к пути ```/friend/waiting/```

```Bash
    curl -u 'masha:678' --request GET --location 'http://0.0.0.0:8000/friend/waiting/'
```
Ответ:
```Bash
    {"sent":[{"id":9,"from_user":{"username":"masha"},
                      "to_user":{"username":"sasha"},
                      "created_at":"2023-05-09T19:48:55.749076Z"},
            {"id":10,"from_user":{"username":"masha"},
                      "to_user":{"username":"julia"},
                      "created_at":"2023-05-09T19:55:18.374039Z"}],
    "received":[]}
```
Видим, что два запроса имеют статус отправлены, и ни одного полученного.

*Саша решает принять заявку Маши в друзья*

Сначала посмотрим, есть ли у него входящие запросы:
    
```Bash
    curl -u 'sasha:345' --request GET --location 'http://0.0.0.0:8000/friend/waiting/'
```

Видим, что есть:
```Bash
    {"sent":[],
    "received":[{"id":9,"from_user":{"username":"masha"},
                        "to_user":{"username":"sasha"},
                        "created_at":"2023-05-09T19:48:55.749076Z"}]}
```    

Чтобы, принять заявку обратимся к пути: ```friendship/<int:request_id>/accept/``` (ID получили из предыдущего ответа)

```Bash
    curl -u 'sasha:345' --request POST --location 'http://0.0.0.0:8000/friendship/9/accept/'
```

Получаем ответ, что два пользователя теперь друзяшки:

```Bash
    {"id":1,"user1":{"username":"masha"},
            "user2":{"username":"sasha"},
            "created_at":"2023-05-09T20:24:46.500317Z"}
```


*Юля решает отклонить заявку Маши в друзья (ох уж эти женщины)*

Опять смотрим, есть ли у нас входящие запросы:
```Bash
    curl -u 'julia:123' --request GET --location 'http://0.0.0.0:8000/friend/waiting/'
```

Отклоняем запрос по такому пути:
```Bash
    curl -u 'julia:123' --request POST --location 'http://0.0.0.0:8000/friendship/10/reject/'
```
А в ответ только тишина и статус код 204. Больше их ничего не связывает :(

*На сцену выходит Вася и отправляет заявку в друзья Саше*

```Bash
    curl -u 'vasya:789' --request POST --location 'http://0.0.0.0:8000/friend/sasha/request/'
```

Теперь он хочет посмотреть принял он заявку или нет:
```Bash
    curl -u 'vasya:789' --request GET --location 'http://0.0.0.0:8000/friend/sasha/status/'
```
В ответ он видит, что Саша всё ещё тупит и не принимает заявку:
```Bash
    {"status":"Outgoing request"}
```
Саша не заметил заявки от Васи и сам направил заявку к нему:
    
```Bash
  curl -u 'sasha:345' --request POST --location 'http://0.0.0.0:8000/friend/vasya/request/'
```
В ответ он удивленно получает, что пользователи теперь друзья:
```Bash
  {"id":2,"user1":{"username":"sasha"},
          "user2":{"username":"vasya"},
          "created_at":"2023-05-10T09:45:02.389409Z"}
```
Ну и наконец для полноты картины удалим Васю из друзей Саши:
```Bash
  curl -u 'sasha:345' --request DELETE --location 'http://0.0.0.0:8000/friend/vasya/remove/'
```
Ответ 204...
