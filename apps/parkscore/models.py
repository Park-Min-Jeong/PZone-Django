from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

# Create your models here.

# class support(models.Model):
#     writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     writeDT = models.DateTimeField(auto_now_add=True)
#     title = models.TextField()
#     question = models.TextField()
#     answer = models.TextField(null=True)
#     answered = models.IntegerField(choices=[(1, "y"), (0, "n")])