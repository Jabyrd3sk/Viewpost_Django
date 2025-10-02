from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate with either username or email"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Try to fetch the user by username or email (case‑insensitive).
        try:
            user = User.objects.get(
                Q(username__iexact=username) |
                Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None

        # Use the default password check
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None