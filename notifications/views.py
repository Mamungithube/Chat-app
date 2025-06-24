from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [{
        'id': n.id,
        'message': n.message,
        'created_at': n.created_at.isoformat(),
        'is_read': n.is_read
    } for n in notifications]
    return JsonResponse({'notifications': data})

@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)