from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows logging in using either 
    the unique email address or the username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if not username or not password:
            return None

        # Look up user by email first (since email is unique), then by username
        users = User.objects.filter(Q(email__iexact=username) | Q(username__iexact=username))
        
        for user in users:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
