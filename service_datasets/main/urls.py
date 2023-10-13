from django.urls import path
from . import views
from .views import LoginUser, RegisterUser

urlpatterns = [
    path('', views.index, name='start'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('download-dataset', views.download_dataset, name='download-dataset'),
    path('downloads/<int:id>', views.downloaded_file, name='downloaded-file'),
    path('downloads/<int:id>/filter', views.set_filter, name='set-filter'),
    path('downloads/<int:id>/sorting', views.sorting, name='sorting'),
    path('delete/<int:id>', views.delete_file, name='delete-file'),
]
