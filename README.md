## Команды:

1. Запустить базу данных в docker
```
docker-compose up -d
```
2. Запустить приложение
```
python app.py
```

## Домашнее задание к лекции «Aiohttp»
## REST API (backend) для сайта объявлений

### Реализованы:

методы создания (POST) /редактирования (PATCH) / удаления (DELETE) объявления.    

У объявления (post) есть следующие поля: 
- заголовок ('title')
- описание ('content')
- дата создания ('created')
- владелец ('user_id')

#### Для того, чтобы создать объвление, предварительно нужно создать пользователя (авторизоваться):
POST-запрос (на '/users/') с уникальными 'username', 'email', 'password'.

#### Для создания объявления:
POST-запрос (на '/posts/') с обязательными полями 'title', 'content', 'user_id' 
('user_id' должен соответствовать id того пользователя, который отправляет запрос).
В headers обязательно передавать username и password.
Создавать объявления может авторизованный пользователь (см.выше)

#### Для редактирования объявления:
PATCH-запрос (на '/posts/<post_id>').
В headers обязательно передавать username и password.
Редактировать объвление может только автор объявления.

#### Для удаления объявления:
DELETE-запрос (на '/posts/<post_id>').
В headers обязательно передавать username и password.
Удалять объвление может только автор объявления.