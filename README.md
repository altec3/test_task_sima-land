### Тестовое задание

*Стек:*
* Python: 3.11
* aiohttp: 3.8.4
* PostgreSQL: 14
* SQLAlchemy: 2.0.15  

*Среда разработки: PyCharm*

---
### Описание задания
...
* TODO: Реализовать документацию

---
#### Для проверки задания (IDE PyCharm):  
`Требования:`  
* [обязательно] установленная платформа [Docker](https://docs.docker.com/get-docker/)

1. Рядом с файлом *docker-compose.yaml* положить файл *.env* с параметрами приложения (см. файл [.env.example](.env.example)):
2. Собрать и запустить контейнеры с backend (aiohttp) и базой данных (БД):
```python
docker-compose up --build -d
```
В результате будет собран и запущен контейнер с работающим приложением, а так же скачан и запущен контейнер с БД PostgreSQL. 
При запуске приложения будет создан пользователь с админскими правами (логин и пароль из файла *.env*).

Посмотреть список запущенных контейнеров можно командой:
```python
docker-compose ps
```

Остановить контейнеры:
```python
docker-compose down
```
