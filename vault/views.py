from django.shortcuts import render ,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import base64
from cryptography.fernet import Fernet
from .models import UserProfile
from .models import EncryptedFile


@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_key = user_profile.get_decrypted_key()
    return render(request, 'vault/dashboard.html', {'key': user_key})
    

def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            redirect('login')
    else:
        form=UserCreationForm
    return render(request,'vault/register.html',{'form':form})


@login_required
def upload_page(request):
    return render(request, 'vault/upload_page.html')

@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        aes_key = base64.b64decode(request.POST['aes_key'])
        iv = base64.b64decode(request.POST['iv'])

        # Encrypt AES key with user's per-user key
        user_key = request.user.userprofile.get_decrypted_key()
        f = Fernet(user_key)
        encrypted_aes_key = f.encrypt(aes_key)

        encrypted = EncryptedFile.objects.create(
            owner=request.user,
            file=uploaded_file,
            encrypted_aes_key=encrypted_aes_key,
            original_name=uploaded_file.name.replace(".enc", ""),
            iv=iv
        )
        return JsonResponse({'status': 'ok'},status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def file_list(request):
    files = EncryptedFile.objects.filter(owner=request.user).order_by('-upload_time')
    return render(request, 'vault/file_list.html', {'files': files})

@login_required
def download_file(request, file_id):
    pass
