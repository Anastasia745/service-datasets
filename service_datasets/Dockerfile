FROM python:3.10.9

RUN pip install kaggle

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir sd

WORKDIR sd

ADD . /sd/

ADD .env.docker /sd/.env

COPY kaggle.json /root/.kaggle/kaggle.json
RUN chmod 600 /root/.kaggle/kaggle.json

ENV KAGGLE_CONFIG_DIR=/root/.kaggle

ENV APP_NAME=SERVICE_DATASETS

RUN apt-get update && apt-get install -y --no-install-recommends gunicorn

RUN pip install -r requirements.txt

RUN python manage.py migrate
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'Almazik111999')" | python manage.py shell

CMD gunicorn service_datasets.wsgi:application -b 0.0.0.0:8000
