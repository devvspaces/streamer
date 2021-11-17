import threading
import logging
# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')

# from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, CreateView, ListView

from .models import Stream
from .utils import MediaLink

class AudioHome(ListView):
    template_name = 'poc/stream_list.html'

    extra_context = {
        'title': 'Audio Streams'
    }

    model = Stream
    context_object_name = 'streams'


class AudioStreamDetail(DetailView):
    template_name = 'poc/index.html'

    model = Stream
    slug_url_kwarg = 'id'
    slug_field = 'id'

    extra_context = {
        'title': 'Audio Stream Detail'
    }

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        obj = self.get_object()

        streams = obj.result_set.all()

        context['streams'] = streams

        context['room_name'] = str(obj.id)

        return context

class CreateAudioStream(CreateView):
    template_name = 'poc/create.html'

    model = Stream
    fields = '__all__'

    extra_context = {
        'title': 'Audio Stream Create'
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        obj = MediaLink(stream=self.object)

        t1 = threading.Thread(target=obj.process)
        t1.start()

        return response