from django.urls import path

from . import views

urlpatterns = [
    path('', views.AudioHome.as_view(), name='home'),
]
