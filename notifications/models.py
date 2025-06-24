from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
from django.db import models
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder

# class SafeJSONField(models.JSONField):
#     def get_prep_value(self, value):
#         try:
#             if isinstance(value, str):
#                 # Try to parse if it's a string
#                 import json
#                 return json.loads(value)
#             return super().get_prep_value(value)
#         except (TypeError, ValueError, json.JSONDecodeError):
#             # If invalid, store as wrapped JSON
#             return {'raw_value': str(value)}

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=50, null=True, blank=True)  # Stores the JSON content
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']