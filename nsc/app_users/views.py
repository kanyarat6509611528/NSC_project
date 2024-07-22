from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from app_users.forms import RegisterForm, UserProfileForm
from app_users.models import CustomUser, UserPhobias
from app_general.models import Phobias
from app_users.utils.activation_token_generator import activation_token_generator

# Create your views here.

def register(request: HttpRequest):
    # POST
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Register and wait for activation
            user: CustomUser = form.save(commit=False)
            user.is_active = False
            user.save()

            # Build email body
            context = {
                "protocol": request.scheme,
                "host": request.get_host(),
                "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
                "token": activation_token_generator.make_token(user),
            }
            email_body = render_to_string(
                "app_users/activate_email.html", context=context
            )

            # Send email
            email = EmailMessage(
                to=[user.email],
                subject="เปิดใช้งานบัญชีบน AI PICK Phobia System", # หัวข้อในอีเมล
                body=email_body,
            )
            email.send()

            # Change redirect to register thank you
            return HttpResponseRedirect(reverse("register_thankyou"))
    else:
        form = RegisterForm()

    # GET
    context = {"form": form}
    return render(request, "app_users/register.html", context)

# --------------------------------------------------------------------------- 

def register_thankyou(request: HttpRequest):
    return render(request, "app_users/register_thankyou.html")

# --------------------------------------------------------------------------- 

def activate(request: HttpRequest, uidb64: str, token: str):
    title = "Activate account เรียบร้อย"
    content = "คุณสามารถเข้าสู่ระบบได้เลย"
    id = urlsafe_base64_decode(uidb64).decode()
    try:
        user = CustomUser.objects.get(id=id)
        if not activation_token_generator.check_token(user, token):
            raise Exception("Check token false")
        user.is_active = True
        user.save()
    except:
        print("Activate ไม่ผ่าน")
        title = "Activate account ไม่ผ่าน"
        content = "เป็นไปได้ว่าลิ้งค์ไม่ถูกต้อง หรือหมดอายุไปแล้ว"

    context = {"title": title, "content": content}
    return render(request, "app_users/activate.html", context)

# --------------------------------------------------------------------------- 

@login_required
def profile(request: HttpRequest):
    user = request.user

    # POST
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            response = HttpResponseRedirect(reverse("profile"))
            response.set_cookie("is_saved", "1")
            return response
    else:
        form = UserProfileForm(instance=user)

    # GET
    is_saved = request.COOKIES.get("is_saved") == "1"
    flash_message = "บันทึกเรียบร้อย" if is_saved else None
    user_phobias = UserPhobias.objects.filter(user=user)
    
    context = {
        "form": form,
        "flash_message": flash_message,
        'user': user,
        'user_phobias': user_phobias,
    }
    response = render(request, "app_users/profile.html", context)
    if is_saved:
        response.delete_cookie("is_saved")
    return response

# ---------------------------------------------------------------

@login_required
def user_select(request):
    user = request.user
    user_phobias = UserPhobias.objects.filter(user=user)
    phobias = Phobias.objects.all().order_by('name_ENG')

    # Handle POST request
    if request.method == 'POST':
        if 'save' in request.POST:
            phobia_ids = request.POST.getlist('phobias')
            for phobia_id in phobia_ids:
                phobia = Phobias.objects.get(pk=phobia_id)
                if not UserPhobias.objects.filter(user=user, phobia=phobia).exists():
                    UserPhobias.objects.create(user=user, phobia=phobia)
            return redirect('user_select')
        elif 'delete' in request.POST:
            phobia_ids_to_delete = request.POST.getlist('phobia_ids_to_delete')
            UserPhobias.objects.filter(id__in=phobia_ids_to_delete).delete()
            return redirect('user_select')

    # Exclude already selected phobias from the list
    available_phobias = []
    for phobia in phobias:
        if not user_phobias.filter(phobia=phobia).exists():
            available_phobias.append(phobia)

    # Prepare context for rendering template
    context = {
        'user_phobias': user_phobias,
        'phobias': available_phobias,  # Pass filtered list to template
    }
    return render(request, 'app_users/user_select.html', context)