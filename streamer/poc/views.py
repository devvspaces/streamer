from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from django.urls import reverse
from django.http import JsonResponse

class AudioHome(TemplateView):
    template_name = 'poc/index.html'

    extra_context = {
        'title': 'AUdio Streamer'
    }