from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainView.as_view()),
    path('admin/', admin.site.urls),
]
