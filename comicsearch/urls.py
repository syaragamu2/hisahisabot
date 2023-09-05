from django.urls import path
from .views import linebot
urlpatterns = [
    #...
    path("webhook/", linebot, name="comicsearch-webhook"),
]