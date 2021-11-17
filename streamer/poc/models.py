from django.db import models
from django.urls.base import reverse

# Create your models here.
class Stream(models.Model):
    link = models.URLField()

    def __str__(self):
        return self.link

    def get_absolute_url(self):
        return reverse("poc:stream_detail", kwargs={"id": self.id})
    
class Result(models.Model):
    key = models.IntegerField()
    title = models.CharField(max_length=200)
    layout = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    url = models.URLField()

    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.key