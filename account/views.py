from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
from caesers import caesar_encrypt, caesar_decrypt  # Import encryption and decryption functions


def check_credentials(request):
    """Helper function to authenticate user with encrypted email and raw password."""
    encrypted_email = caesar_encrypt(request.POST.get('email'))
    password = request.POST.get('password')
    return EmailBackend.authenticate(request, username=encrypted_email, password=password)


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = check_credentials(request)
        if user is not None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)

            # Encrypt sensitive fields before saving
            user.first_name = caesar_encrypt(user.first_name)
            user.last_name = caesar_encrypt(user.last_name)
            user.email = caesar_encrypt(user.email)
            voter.admin = user

            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))


def account_dashboard(request):
    """Ensure decrypted values are passed to the dashboard template."""
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access the dashboard.")
        return redirect(reverse("account_login"))

    user = request.user
    context = {
        'first_name': caesar_decrypt(user.first_name),
        'last_name': caesar_decrypt(user.last_name),
        'email': caesar_decrypt(user.email),
    }
    return render(request, "voting/dashboard.html", context)
