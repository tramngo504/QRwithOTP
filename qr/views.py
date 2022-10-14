from multiprocessing import context
from django.shortcuts import render
import random
import smtplib
import qrcode
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm

otp_qr = 0
otp_mail = 0

def welcome(request):
	return render(request, 'welcome.html')
def validateuser(request):
    username = request.POST.get("t1")
    password = request.POST.get("t2")

    if username == "tram" and password == "tram":
        randnum = random.randint(000000,999999)
        global otp_qr
        otp_qr = randnum
        im = qrcode.make("OTP: " +str(randnum))
        im.save(r'qr/static/images/qrimage.jpg')
        return render(request, 'qrcode_page.html')
    else:
        return render(request, 'login.html', {"message":"Invalid User"})

def validateOTP(request):
    user_otp = request.POST.get('otp')
    if user_otp == str(otp_qr):
        return render(request, 'welcome.html')
    else:
        return render(request, "login.html", {"message": "Invalid OTP"})

def validate_mail(request):
	if request.method == 'POST':
		user_otp = request.POST.get('otp_mail')
		if user_otp == str(otp_mail):
			return render(request, 'welcome.html')
		else:
			return render(request, "register.html", {"message": "Invalid OTP"})

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
			validate_register()
			return render(request, "validate_mail.html")
			# return redirect('login')
		

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
				global otp_qr
				otp_qr = randnum
				im = qrcode.make("OTP: " +str(randnum))
				im.save(r'qr/static/images/qrimage.jpg')
				return render(request, 'qrcode_page.html')
		else:
			messages.info(request, 'Username OR password is incorrect')
	context = {}
	return render(request, 'login.html', context)


def validate_register():
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.starttls()
	server.login('tramngo504@gmail.com', 'fizdaofigoenqnve')
	otp = ''.join([str(random.randint(0,9)) for i in range(4)])
	print(otp)
	global otp_mail
	otp_mail = otp
	msg = 'Hello! Your OTP is ' + str(otp)
	server.sendmail('tramngo504@gmail.com', 'tramngo0381@gmail.com',msg)
	server.quit()


def logoutUser(request):
	logout(request)
	return redirect('login')

