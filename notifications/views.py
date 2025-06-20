# views.py
from django.contrib.auth.decorators import user_passes_test
from .utils import send_global_notification
from django.http import JsonResponse
from django.shortcuts import render

def my_json_view(request):
    data = {
        'message': 'This is a JSON response from Django!',
        'status': 'success',
        'items': [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'}
        ]
    }
    return JsonResponse(data)


@user_passes_test(lambda u: u.is_superuser)
def send_global_notification_view(request):
    if request.method == "POST":
        message = request.POST.get("message")
        send_global_notification(message)
        return JsonResponse({"status": "success"})
    return render(request, "admin/send_notification.html")