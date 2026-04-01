from django.shortcuts import render, redirect
from userapp.models import userModel
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, 'mainapp/main-home.html')

def about(request):
    return render(request, 'mainapp/main-about.html')

def contact(request):
    return render(request, 'mainapp/main-contact.html')

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            if username == "admin" and password == "admin":
                messages.success(request, 'Admin has successfully logged in!')
                return redirect("admin_dash")
        except:
            return redirect("admin_login")
    return render(request, 'mainapp/main-admin-login.html')

def user_register(request):
    if request.method == "POST" and request.FILES["image"]:
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("pwd")
        address = request.POST.get("address")
        image = request.FILES["image"]
        userModel.objects.create(name=name, email=email, phone=phone, password=password, address=address, image=image)
        messages.success(request, 'You have successfully registered!')
        return redirect('user_login')
    return render(request, 'mainapp/main-user-register.html')