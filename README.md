# Инструкция по развёртыванию приложения

Предварительно для получения имени пользователя username и генерации ключа key, нужно зарегистрироваться на https://www.kaggle.com.

## Без использования Dockerfile

1. При необходимости установить Python (https://www.python.org/downloads/);
2. Скачать приложение:
```
git clone -b master https://github.com/Anastasia745/service-datasets.git
```
3. Заменить в файле kaggle.json и main/settings.py параметры username и key на собственные;
4. Перейти в папку проекта и выполнить:
```
cd service_datasets
```
5. Установить виртуальное окружение:
```
python -m venv venv
```
6. Установить зависимости:
```
pip install -r requirements.txt
```
7. Сделать миграции:
```
python manage.py migrate
```
8. Создать супер пользователя для администрирования. Ввесити имя пользователя и пароль (не менее 8 символов, должны присутствовать и буквы, и цифры):
```
python manage.py createsuperuser
```
9. Запустить приложение:
```
python manage.py runserver
```
В терминале появится ссылка, по которой можно открыть приложение.

## С использованием Dockerfile

1. Установить Docker (https://docs.docker.com/get-docker/);
3. Скачать приложение:
```  
git clone -b master https://github.com/Anastasia745/service-datasets.git
```
3. Заменить в файле kaggle.json и main/settings.py параметры username и key на собственные;
5. При желании, в Dockerfile в строке ```RUN echo "from django.contrib.auth ...``` изменить данные супер пользователя; 
7. Перейти в папку проекта и выполнить:
```
cd service_datasets
```
6. Для Windows запустить Docker Desktop;
8. Сбилдить Docker-образ:
```
docker build . --file Dockerfile --tag image-tag
```
8. Запустить образ:
```
docker run -p 8001:8000 image-tag
```
Приложение можно открыть, введя в адресной строке localhost:8001.
