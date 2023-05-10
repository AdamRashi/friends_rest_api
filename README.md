#Django-сервис друзей
Этот проект представляет собой Django-сервис друзей, который позволяет пользователям зарегистрироваться, отправлять и принимать заявки в друзья, управлять списком своих друзей и многое другое.

##Запуск проекта
Для начала склонируйте репозиторий
```bash
git clone https://github.com/AdamRashi/friends_rest_api
```

Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv env
source env/bin/activate
```

Установите зависимости:

```shell
pip install -r requirements.txt
```

Запустите миграции базы данных:

```bash
python manage.py makemigrations
python manage.py migrate
```

##Использование
Запустите сервер с помощью команды:

```bash
python manage.py runserver
```

API сервиса будет доступно на `http://localhost:8000/api/`

Вы можете использовать интерфейс Swagger для взаимодействия с API. Для этого перейдите на http://localhost:8000/swagger/.

Для аутентификации и получения токена отправьте POST запрос на http://localhost:8000/api/token/ с параметрами username и password.

###Документация API
Документация API доступна в файле openapi.yml. Она также может быть найдена на странице Swagger интерфейса.
Более подробное описание и примеры использования API вы можете найти в папке `docs/`

##Docker
Вы можете запустить этот сервис в контейнере Docker. Для этого выполните следующие шаги:

Соберите Docker образ:

```bash
docker build -t <название образа> .
```

Запустите контейнер:

```bash
docker run -d -p <порт на вашем ПК>:8000 --name <название контейнера> <название образа>

```
Пример:
```shell
docker build -t friends_api .
docker run -d -p 8080:8000 --name api friends_api
```
В данном примере API сервиса будет доступно на http://localhost:8080/api/

Также, в дополнение к команде `run`, можно указать переменные окружения, например:

```shell
docker run -d -p 8080:8000 --name api friends_api -e SECRET_KEY=<ваш ключ>\
-e DJANGO_SUPERUSER_USERNAME=<username админа> \
-e DJANGO_SUPERUSER_EMAIL=<почта> \
-e DJANGO_SUPERUSER_PASSWORD=<пароль>
```
По умолчанию, создаётся аккаунт администратора со следующими данными:
```python
DJANGO_SUPERUSER_USERNAME='admin'
DJANGO_SUPERUSER_EMAIL='admin@example.com'
DJANGO_SUPERUSER_PASSWORD='adminpassword'
```



