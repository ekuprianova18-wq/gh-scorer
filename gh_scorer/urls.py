from django.contrib import admin
from django.urls import path
from scorer_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('repo/<int:repo_id>/', views.detail, name='detail'),
    path('add/', views.add_repo, name='add_repo'),
    path('update/<int:repo_id>/', views.update_repo, name='update_repo'),
]