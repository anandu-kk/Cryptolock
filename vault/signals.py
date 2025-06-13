from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import EncryptedFile
import os

@receiver(post_delete, sender=EncryptedFile)
def delete_encrypted_file_on_delete(sender, instance, **kwargs):
    """
    Deletes the associated file from the filesystem when an EncryptedFile instance is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)