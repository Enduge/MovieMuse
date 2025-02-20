from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UpdateAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']