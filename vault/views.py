from django.shortcuts import render ,redirect ,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
import base64
from cryptography.fernet import Fernet
from .models import UserProfile,EncryptedFile,AccessLog


@login_required
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
        user_profile.generate_user_key()
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

        AccessLog.objects.create(
            user=request.user,
            file_name=encrypted.original_name,
            action='upload'
        )

        return JsonResponse({'status': 'ok'},status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def file_list(request):
    files = EncryptedFile.objects.filter(owner=request.user).order_by('-upload_time')
    return render(request, 'vault/file_list.html', {'files': files})


@login_required
def download_file(request, file_id):
    file=get_object_or_404(EncryptedFile, id=file_id, owner=request.user)
    user_key = request.user.userprofile.get_decrypted_key()
    fernet = Fernet(user_key)
    encrypted_aes_key = file.encrypted_aes_key
    # Handle Postgres (memoryview), None, or other types
    if encrypted_aes_key is None:
        raise ValueError("Encrypted AES key is missing.")
    if isinstance(encrypted_aes_key, memoryview):
        encrypted_aes_key = encrypted_aes_key.tobytes()
    elif not isinstance(encrypted_aes_key, (bytes, str)):
        raise TypeError(f"encrypted_aes_key must be bytes, str, or memoryview, got {type(encrypted_aes_key)}")
    decrypted_aes_key = fernet.decrypt(encrypted_aes_key)

    with file.file.open('rb') as f:
        encrypted_data = f.read()
    
    AccessLog.objects.create(
            user=request.user,
            file_name=file.original_name,
            action='download'
        )

    return JsonResponse({
        'filename': file.original_name,
        'encrypted_data': base64.b64encode(encrypted_data).decode(),
        'aes_key': base64.b64encode(decrypted_aes_key).decode(),
        'iv': base64.b64encode(file.iv).decode()
    })


@login_required
def delete_file(request,file_id):
    if request.method=='DELETE':
        file=get_object_or_404(EncryptedFile,id=file_id,owner=request.user)
        AccessLog.objects.create(
            user=request.user,
            file_name=file.original_name,
            action='delete'
        )
        file.delete()

        return JsonResponse({'status': 'ok'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)