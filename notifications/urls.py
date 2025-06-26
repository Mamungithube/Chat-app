from django.urls import path
from . import views, consumers

urlpatterns = [
    path("notifications/send/", views.send_notification_api),

]