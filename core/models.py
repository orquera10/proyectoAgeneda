from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class Role(models.TextChoices):
        EDITOR = 'editor', 'Editor'
        LECTOR = 'lector', 'Lector'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LECTOR)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
