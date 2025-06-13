from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard,name='dashboard'),
    path('register/',views.register,name='register'),
    path('upload/',views.upload_page,name='upload_page'),
    path('upload_file/',views.upload_file,name='upload_file'),
    path('file_list/',views.file_list,name='file_list'),
    path('download_file/<int:file_id>/', views.download_file, name='download_file'),
]
