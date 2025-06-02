# Foodgram

Фудграм — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

## Как запустить?

### Локальный запуск серверной части

Для дебага можно запустить локально только серверную часть. Для этого нужно:
0) Убедиться, что у вас установлен питон :)
1) Склонировать репозиторий
```
git clone https://github.com/maximister/foodgram-st.git
```
2) Создать и активировать окружение:
```shell
cd foodgram-st/backend
python -m venv venv
venv\Scripts\activate           # для Windows
source venv/bin/activate        # для Linux/Mac/bash-терминала
```
3) Установить зависимости:
```shell
pip install -r requirements.txt
```
4) Провести миграцию бд:
```
python manage.py makemigration
python manage.py migrate
```
5) Наполнить бд тестовыми ингредиентами:
```
python manage.py fill_database_with_default_ingredients
```
6) 6. Запустить сервер
```
python manage.py runserver
```

Сервер будет доступен по адресу [http://localhost:8000/](http://localhost:8000/)

**Примечания**:
* При локальном запуске можно использовать SQLite (установить DEBUG=True в settings.py приложения foodgram);
* Для очистки локальной базы после тестов предусмотрен скрипт /postmal_collection/clear_db.sh

### Локальный запуск всего проекта
Также можно развернуть весь проект с помощью docker-compose. Для этого нужно:
1) Перейти в папку /infra
```
cd infra
```
2) Создать .env файл и наполнить его по образцу .env.example
3) Запустить приложение:
```
docker-compose up
#или для запуска в фоновом режиме
docker-compose up -d
```
## Я хочу просто потыкать приложение
Пока автора не уволили с работы, развернутое приложение доступно по следующему адресу: [http://51.250.19.165/](http://51.250.19.165/)

Для изучения приложения можно ознакомиться со следующими эндпоинтами:
- Веб-приложение:
    - локально [http://localhost/](http://localhost/)
    - удаленно [http://51.250.19.165/](http://51.250.19.165/)
- API Документация:
    - локально [http://localhost/api/docs/](http://localhost/api/docs/)
    - удаленно [http://51.250.19.165/api/docs/](http://51.250.19.165/api/docs/)
- Панель администратора:
    - локально [http://localhost/admin/](http://localhost/admin/)
    - удаленно [http://51.250.19.165/admin/](http://51.250.19.165/admin/)
- API Endpoints:
    - локально [http://localhost/api/](http://localhost/api/)
    - удаленно [http://51.250.19.165/api/](http://51.250.19.165/api/)

