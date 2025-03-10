from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = ResizedImageField(size=[250, 250], default='default.png', upload_to='profile_images')

    def __str__(self):
        return self.user.username


class Movie(models.Model):
    imdb_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    poster = models.URLField(max_length=500, blank=True, null=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    rated = models.CharField(max_length=20, blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.year})"


class MovieReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_reactions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only have one reaction per movie
        unique_together = ['user', 'movie']
        
    def __str__(self):
        return f"{self.user.username} {self.reaction_type}d {self.movie.title}"
