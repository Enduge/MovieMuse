from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField

class Profile(models.Model, ResizedImageField):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = ResizedImageField(size=[250, 250], default='default.png', upload_to='profile_images')

    def __str__(self):
        return self.user.username


