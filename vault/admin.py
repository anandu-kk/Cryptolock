from django.contrib import admin
from .models import UserProfile, EncryptedFile, AccessLog

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(EncryptedFile)
admin.site.register(AccessLog)
