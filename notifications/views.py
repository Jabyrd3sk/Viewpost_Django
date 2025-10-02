from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    #notifications = Notification()
    # Mark all unread as read
    request.user.notifications.filter(read=False).update(read=True)
    # Grab all notifications
    qs = request.user.notifications.all()
    return render(request, 'notifications/list.html', {'notifications': qs})