import os
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta
import random
class Profile(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            # отримуємо старий об'єкт із БД
            old_profile = Profile.objects.get(pk=self.pk)
            if old_profile.avatar and old_profile.avatar != self.avatar:
                # видаляємо старий файл аватара
                if os.path.isfile(old_profile.avatar.path):
                    os.remove(old_profile.avatar.path)
        except Profile.DoesNotExist:
            pass  # якщо об'єкта ще немає — нічого не робимо
        super().save(*args, **kwargs)




class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ", ".join([user.username for user in self.participants.all()])

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"

class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username



def generate_code():
    return str(random.randint(100000, 999999))

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default=generate_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < datetime.now() - timedelta(minutes=30)  # код дійсний 30 х





class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)