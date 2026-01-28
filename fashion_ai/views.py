from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required

def superuser_required(user):
    return user.is_authenticated and user.is_superuser

def login_view_redirect(request):
    if request.user.is_authenticated:
        return redirect("/api/")
    return redirect("/login/")

def login_view(request):
    if request.user.is_authenticated:
        return redirect("/api/")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
              messages.success(request, "Admin logged in successfully")
            else:
              messages.success(request, "User logged in successfully")

            return redirect("/api/")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

@user_passes_test(superuser_required, login_url="/login/")
def register_view(request):
    """
    Only SUPERUSER can create new users
    """

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # 🔹 Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("/register/")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("/register/")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("/register/")

        # 🔹 Create user (no auto-login)
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "User created successfully")
        return redirect("/api/")

    return render(request, "register.html")