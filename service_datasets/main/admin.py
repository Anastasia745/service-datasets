from django.contrib import admin
from .models import Files, Datasets

admin.site.register(Datasets)
admin.site.register(Files)