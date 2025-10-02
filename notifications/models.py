from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class Notification(models.Model):
    # Who gets notified
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    # Who did the action
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actor_notifications')
    # e.g 'liked ur post', 'commented on ur post', 'started following u'
    verb = models.CharField(max_length=255)
    # target object (Post, Comment, Profile)
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_ct', 'target_id')

    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']