from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Picture(models.Model):
    image = models.JSONField()
    palette = models.JSONField(default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    public = models.BooleanField(default=False)
    timestamp = models.DateTimeField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return f"Picture {self.pk} by {self.user}"

class Tag(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name="tags")
    tag = models.CharField(max_length=50)