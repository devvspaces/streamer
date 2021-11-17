from django.urls import path

from . import views

app_name = 'poc'
urlpatterns = [
    path('', views.AudioHome.as_view(), name='home'),
    path('streams/create/', views.CreateAudioStream.as_view(), name='stream_create'),
    path('streams/<int:id>/', views.AudioStreamDetail.as_view(), name='stream_detail'),
]
