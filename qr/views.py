from multiprocessing import context
import re
from django.shortcuts import render
import random
import qrcode
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm

otp = 0
# # Create your views here.
# def loginPage(request):
#     context = {}
#     return render(request, 'login.html', context)

# def registerPage(request):
#     context = {}
#     return render(request)

def welcome(request):
	return render(request, 'welcome.html')
def validateuser(request):
    username = request.POST.get("t1")
    password = request.POST.get("t2")

    if username == "tram" and password == "tram":
        randnum = random.randint(000000,999999)
        global otp
        otp = randnum
        im = qrcode.make("OTP: " +str(randnum))
        im.save(r'qr/static/images/qrimage.jpg')
        return render(request, 'qrcode_page.html')
    else:
        return render(request, 'login.html', {"message":"Invalid User"})

def validateOTP(request):
    user_otp = request.POST.get('otp')
    if user_otp == str(otp):
        return render(request, 'welcome.html')
    else:
        return render(request, "login.html", {"message": "Invalid OTP"})

def registerPage(request):
	# if request.user.is_authenticated:
	# 	return redirect('home')
	# else:
	# 	form = CreateUserForm()
	# 	if request.method == 'POST':
	# 		form = CreateUserForm(request.POST)
	# 		if form.is_valid():
	# 			form.save()
	# 			user = form.cleaned_data.get('username')
	# 			messages.success(request, 'Account was created for ' + user)

	# 			return redirect('login')
			

	# 	context = {'form':form}
	# 	return render(request, 'register.html', context)

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created for ' + user)

			return redirect('login')
		

	context = {'form':form}
	return render(request, 'register.html', context)

def loginPage(request):
	# if request.user.is_authenticated:
	# 	return redirect('home')
	# else:
	# 	if request.method == 'POST':
	# 		username = request.POST.get('username')
	# 		password =request.POST.get('password')

	# 		user = authenticate(request, username=username, password=password)

	# 		if user is not None:
	# 				login(request, user)
	# 				randnum = random.randint(000000,999999)
	# 				global otp
	# 				otp = randnum
	# 				im = qrcode.make("OTP: " +str(randnum))
	# 				im.save(r'qr/static/images/qrimage.jpg')
	# 				return render(request, 'qrcode_page.html')
	# 		else:
	# 			messages.info(request, 'Username OR password is incorrect')
	# 	context = {}
	# 	return render(request, 'login.html', context)
	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
				login(request, user)
				randnum = random.randint(000000,999999)
				global otp
				otp = randnum
				im = qrcode.make("OTP: " +str(randnum))
				im.save(r'qr/static/images/qrimage.jpg')
				return render(request, 'qrcode_page.html')
		else:
			messages.info(request, 'Username OR password is incorrect')
	context = {}
	return render(request, 'login.html', context)
def logoutUser(request):
	logout(request)
	return redirect('login')

