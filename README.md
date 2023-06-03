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
* TODO: Упаковать в docker
* TODO: Реализовать документацию

---
#### Для проверки задания (IDE PyCharm):  
`Требования:`  
* [обязательно] установленная платформа [Docker](https://docs.docker.com/get-docker/)

1. При необходимости, изменить настройки в файле [config.yaml](./config/config.yaml)
2. Установить зависимости:
```python
pip install poetry
poetry install
```
3. Запустить образ с PostgreSQL с учетом параметров в файле [config.yaml](./config/config.yaml):
```python
docker run --name psql -e POSTGRES_DB=postgres -e  POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:14-alpine
```
где:  
POSTGRES_DB - имя БД (database),  
POSTGRES_PASSWORD - пароль для доступа к БД (password).  
4. Создать таблицы в БД:  
Выполнить скрипт [init_db.py](./app/dao/database/init_db.py)  
5. Запустить web-server:
```python
python app/main.py
```
