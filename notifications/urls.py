from django.urls import path
from . import views, consumers

urlpatterns = [
    # HTTP endpoints
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # WebSocket endpoint (keep your existing WebSocket routing)
    # path("ws/global-notifications/", consumers.GlobalNotificationConsumer.as_asgi()),
]