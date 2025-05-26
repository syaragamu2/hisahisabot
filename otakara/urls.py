from django.urls import path
from .views import linebot_view
urlpatterns = [
    #...
    path("webhook/", linebot_view, name="linebot_callback"),
]