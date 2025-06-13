import os
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_key = models.BinaryField()

    def generate_user_key(self):
        user_key = Fernet.generate_key()

        master = Fernet(settings.MASTER_KEY.encode())
        self.encrypted_key = master.encrypt(user_key)
        self.save()

    def get_decrypted_key(self):
        master = Fernet(settings.MASTER_KEY.encode())
        return master.decrypt(self.encrypted_key)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        profile.generate_user_key()

class EncryptedFile(models.Model):
    owner= models.ForeignKey(User, on_delete=models.CASCADE)
    file=models.FileField(upload_to='encrypted_files/')
    encrypted_aes_key=models.BinaryField()
    original_name=models.CharField(max_length=255, null=True)
    iv=models.BinaryField()
    upload_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_name} uploaded by {self.owner.username}"

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255, default="Unknown")
    action = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
