from django.urls import path
from .views import upload, show_tasks, dashboard

urlpatterns = [
    path('upload/', upload, name='upload'),
    path('tasks/', show_tasks, name='show_tasks'),
    path('', dashboard, name='dashboard'),
]