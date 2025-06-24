from django.urls import path
from .views import BondlyChatAPIView

urlpatterns = [
    path('chatbot/', BondlyChatAPIView.as_view(), name='bondly-chat'),
]
