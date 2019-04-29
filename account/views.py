from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404,render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from .models import Profile,Order
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


@login_required
def profile(request, username):
    if request.user.is_superuser:
        order_objects=Order.objects.all().order_by('-id')
        return render(request, "admin_profile.html",{'order_objects': order_objects})

    if request.user.username == username:
        profile_obj = get_object_or_404(Profile, user=request.user)
        return render(request, "profile.html", {'profile':profile_obj})
    else:
        return redirect("main:home")


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        # print(user.username)
        # print(user.profile.username)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return render(request, 'registration/account_activation_invalid.html')