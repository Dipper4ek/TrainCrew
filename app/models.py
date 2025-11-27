from django.db import models
from django.contrib.auth.models import User
import os

class Profile(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

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


from django.db import models
from django.contrib.auth.models import User

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