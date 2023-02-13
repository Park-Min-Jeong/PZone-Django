from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.

# class Score(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='Score')
#     message = rate = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(100.0)])
#
