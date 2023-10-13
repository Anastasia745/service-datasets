import io
import json
import zipfile
import pandas as pd
import requests
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from kaggle.api.kaggle_api_extended import KaggleApi

from .forms import AuthenticationForm, RegisterUserForm
from .models import Datasets, Files
from .settings import KAGGLE_USERNAME, KAGGLE_KEY


@login_required(login_url='login')
def index(request):
    api = KaggleApi()
    api.authenticate()
    datasets = api.datasets_list()
    files = Files.objects.filter(user_id=request.user.id)
    return render(request, 'main/index.html', {'datasets': datasets, 'downloaded_files': files})


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'main/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy('start')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'main/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('start')


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def download_dataset(request):
    username = KAGGLE_USERNAME
    key = KAGGLE_KEY
    if request.method == 'POST':
        path = request.POST.get('dataset-path')
        all_datasets = Datasets.objects.filter(user_id=request.user.id)
        path_datasets = []
        for dataset in all_datasets:
            path_datasets.append(dataset.path)

        if path in path_datasets:
            existing_dataset = Datasets.objects.get(user_id=request.user.id, path=path)
            existing_dataset_id = existing_dataset.id
            existing_dataset.delete()
            existing_files = Files.objects.filter(user_id=request.user.id, dataset_id=existing_dataset_id)
            for existing_file in existing_files:
                existing_file.delete()

        new_dataset = Datasets(user_id=request.user.id, path=path)
        new_dataset.save()
        session = requests.Session()
        session.auth = (username, key)
        url = 'https://www.kaggle.com/api/v1/datasets/download/' + path
        download = session.get(url)
        zip_data = io.BytesIO(download.content)

        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file in file_list:
                file_data = zip_ref.read(file).decode('unicode_escape')
                json_file_data = pd.read_csv(io.StringIO(file_data)).to_json(orient='records')
                new_file = Files(user_id=request.user.id, dataset_id=new_dataset.id, name=file, data=json_file_data)
                new_file.save()
        session.close()
    return redirect('start')


@login_required(login_url='login')
def downloaded_file(request, id):
    files = Files.objects.all()
    file = Files.objects.get(id=id)
    df = pd.DataFrame()
    if not (file is None):
        json_data = json.loads(file.data)
        df = pd.DataFrame(json_data).head(n=50)
    filter_columns = df.columns
    sorting_columns = df.columns
    table_html = df.to_html()
    return render(request, 'main/downloads.html',
                  {'files': files, 'curr_file': file, 'sorting_columns': sorting_columns, 'table': table_html,
                   'filter_columns': filter_columns})


@login_required(login_url='login')
def delete_file(request, id):
    file = Files.objects.get(id=id)
    dataset_id = file.dataset_id
    file.delete()
    if Files.objects.filter(user_id=request.user.id, dataset_id=dataset_id).count() == 0:
        dataset = Datasets.objects.get(user_id=request.user.id, id=dataset_id)
        dataset.delete()
    return redirect('start')


@login_required(login_url='login')
@csrf_exempt
def set_filter(request, id=None):
    if request.method == 'POST':
        selected_columns = request.POST.get('checked')
        filters = selected_columns.split(',')
        file = Files.objects.get(id=id)
        json_data = json.loads(file.data)
        df = pd.DataFrame(json_data).head()
        sorting_columns = list(df.columns)
        if len(selected_columns) != 0:
            df = df[filters]
            sorting_columns = filters
        table_html = df.to_html()
        context = {'table': table_html, 'sorting_columns': sorting_columns}
        data = json.dumps(context)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponse('Неверный запрос')


@login_required(login_url='login')
@csrf_exempt
def sorting(request, id):
    if request.method == 'POST':
        selected_sorting_columns = request.POST.get('sorting_checked')
        selected_filter_columns = request.POST.get('filter_checked')
        filters = selected_filter_columns.split(',')
        sorting_columns = selected_sorting_columns.split(',')
        order = request.POST.get('order')
        if order == '1':
            ascending = True
        else:
            ascending = False
        orders = []
        for i in range(len(sorting_columns)):
            orders.append(ascending)
        file = Files.objects.get(id=id)
        json_data = json.loads(file.data)
        df = pd.DataFrame(json_data).head()
        if len(selected_filter_columns) != 0:
            df = df[filters]
        df = df.sort_values(sorting_columns, ascending=orders)
        table_html = df.to_html()
        context = {'table': table_html}
        data = json.dumps(context)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponse('Неверный запрос')

