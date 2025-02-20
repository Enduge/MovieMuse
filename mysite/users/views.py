from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .forms import UpdateAvatarForm

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.info(request, 'Try again! Username or password is incorrect.')

    context = {}
    return render(request, 'users/login.html', context)

def logout_page(request):
    logout(request)
    return redirect('users:login')

def register_page(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("homepage")
    else:
        form = UserCreationForm()
    return render(request,"users/register.html",{"form": form})

@login_required
def profile(request):
    return render(request,'users/profile.html')

@login_required
def change_avatar(request):
    user_profile = request.user.profile

    if request.method == "POST":
        form = UpdateAvatarForm(request.POST,request.FILES,instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
    else:
        form = UpdateAvatarForm(instance=user_profile)
