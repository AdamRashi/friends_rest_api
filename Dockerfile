FROM python:3.10-slim-buster

ENV SECRET_KEY=mysecretkey
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@example.com
ENV DJANGO_SUPERUSER_PASSWORD=adminpassword

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ../friends_api .

RUN python manage.py makemigrations
RUN python manage.py migrate

RUN echo "from django.contrib.auth import get_user_model; \
    User = get_user_model(); \
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', \
    '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" \
    | python manage.py shell

EXPOSE 8000

CMD ["python", "manage.py", "runserver","--insecure", "0.0.0.0:8000"]
