from django.urls import path
from .views import career_chatbot
from . import views

urlpatterns = [
    path("career-chatbot/", career_chatbot, name="career_chatbot"),
]
