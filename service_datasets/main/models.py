from django.db import models


class Datasets(models.Model):
    user_id = models.IntegerField('Пользователь')
    path = models.CharField('Путь', max_length=200)

    def __str__(self):
        return self.path

    class Meta:
        verbose_name = 'Датасет'
        verbose_name_plural = 'Датасеты'


class Files(models.Model):
    user_id = models.IntegerField('Пользователь')
    dataset_id = models.IntegerField('Датасет')
    name = models.CharField('Имя', max_length=100)
    data = models.TextField('Содержимое', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
