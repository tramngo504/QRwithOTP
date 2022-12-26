from multiprocessing import context
from django.shortcuts import render
import random
import smtplib
import qrcode
import cv2
import pandas as pd
import pathlib
import hashlib
from django.shortcuts import render, redirect 
from django.contrib.auth.hashers import make_password
import pyotp, time
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib

import cv2
import pyzbar.pyzbar as pyzbar
from django.http import StreamingHttpResponse

totp = pyotp.TOTP('base32secret3232', interval = 120)
otp_qr = 0
otp_mail = 0
count = 1
user_mail = ''
user_name = ''
count_qr = 1
form = CreateUserForm()
requestPost = HttpRequest()
# login gmail server
def gmail_login(username, password):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.connect("smtp.gmail.com", 587)
    server.starttls()
    server.login(username, password)
    return server


def welcome(request):
	return render(request, 'welcome.html')

def validateOTP(request):
    user_otp = request.POST.get('otp')
    if user_otp == str(otp_qr):
        return render(request, 'welcome.html')
    else:
        return render(request, "login.html", {"message": "Invalid OTP"})

def validate_mail(request):
	if request.method == 'POST':
		user_otp = request.POST.get('otp_mail')
		global form
		global count
		global user_name
		
		if count == 1:
			if totp.verify(user_otp):
				form = CreateUserForm(requestPost)
				form.save()
				user = User.objects.filter(username=user_name)
				return render(request, 'welcome.html', {'user': user})
			else: 
				count += 1
				return render(request, "validate_mail.html")
		elif count == 2:
			request.method == "POST"
			user_otp = request.POST.get('otp_mail')
			
			if totp.verify(user_otp):
				form = CreateUserForm(requestPost)
				form.save()
				user = User.objects.filter(username=user_name)
				return render(request, 'welcome.html', {'user': user})
			else: 
				count += 1
				return render(request, "validate_mail.html")
		# elif count == 3:
		# 	request.method == "POST"
		# 	user_otp = request.POST.get('otp_mail')
		# 	if totp.verify(user_otp):
		# 		form = CreateUserForm(requestPost)
		# 		form.save()
		# 		return render(request, 'welcome.html')
		# 	else: 
		# 		count += 1
		# 		return render(request, "validate_mail.html")
		else:
			return render(request, "login.html", {"message": "Invalid OTP"})
		# user_otp = request.POST.get('otp_mail')
		# if totp.verify(user_otp):
		# 	global form
		# 	form = CreateUserForm(requestPost)
		# 	form.save()
		# 	return render(request, 'welcome.html')
		# else:
		# 	return render(request, "login.html", {"message": "Invalid OTP"})
def check_account(mail):
	try:
		return User.objects.get(email=mail)
	except User.DoesNotExist:
		return False
		# try:
        # 	return User.objects.get(pk=id)
    	# except User.DoesNotExist:
        # 	return False


def registerPage(request):
	form = CreateUserForm()
	if request.method == 'POST':
		request.POST._mutable = True
		mail = request.POST.get('email')
		global user_mail
		user_mail = mail
		password = request.POST.get('password1')
		# password = password.encode('utf-8')
		# hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt(10))
		# hashedPassword = hashlib.md5(password.encode()).hexdigest()
		# request.POST['password1'] = hashedPassword
		# request.POST['password2'] = hashedPassword
		global requestPost 
		requestPost = request.POST
		form_register = CreateUserForm(request.POST)
		
		if form_register.is_valid():
			user = form_register.cleaned_data.get('username')
			if (not check_account(mail)):
				validate_register()
				# form.save()
				return render(request, "validate_mail.html")
			else :
				msg = "Your email has already been registered"
				return render(request, 'login.html', {"error": "1"})
		# 	# form.save()
		# 	global form
		# 	form = form_register
		# 	# user = form.cleaned_data.get('username')
		# 	# messages.success(request, 'Account was created for ' + user)
		# 	validate_register()
		# 	return render(request, "validate_mail.html")
		# 	# return redirect('login')
		

	context = {'form':form}
	return render(request, 'register.html', context)

def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		passw = request.POST.get('password')
		# hashedPassword = hashlib.md5(passw.encode()).hexdigest()
		user = authenticate(request, username=username, password=passw)
		if user is not None:
			user_m = User.objects.get(username=username)
			global user_name
			user_name = username
			user_mail = user_m.email
			login(request, user)
			msg = MIMEMultipart()
			msg['Subject'] = "QR Code"
			msg['From'] = "qrotpcode@gmail.com"
			msg['To'] = user_mail


			# make qr code
			name = ''.join([str(random.randint(0,9)) for i in range(6)])
			randnum = random.randint(000000,999999)
			print(randnum)
			global otp_qr
			otp_qr = randnum
			img = qrcode.make(str(randnum))
			img.save("C:\\Users\\TechCare\\Desktop\\HK7\\PBL\\New folder\\{}.png".format(name))

			file_path = r'C:\Users\TechCare\Desktop\HK7\PBL\New folder'
			file_name = "{}.png".format(name)
			file = open(file_path+"\\"+file_name, "rb")

			payload = MIMEBase('application', 'octet-stream')
			payload.set_payload(file.read())
			file.close()
			encoders.encode_base64(payload)
			payload.add_header('Content-Disposition', 'attachment', filename=file_name)
			msg.attach(payload)

			server = gmail_login("qrotpcode@gmail.com", 'emspzdwcwqfwzezl')
			server.send_message(msg)
			server.quit()
			print("Email has been sent")
			# randnum = random.randint(000000,999999)
			# global otp_qr
			# otp_qr = randnum
			# im = qrcode.make("OTP: " +str(randnum))
			# im.save(r'qr/static/images/qrimage.jpg')
			return render(request, 'readQR.html')

		else:
			messages.info(request, 'Username OR password is incorrect')
	context = {}
	return render(request, 'login.html', context)


def validate_register():
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.starttls()
	server.login('qrotpcode@gmail.com', 'emspzdwcwqfwzezl')
	global otp_mail, totp
	otp = totp.now()
	otp_mail = otp
	SUBJECT = "Authenticate your account!" 
	TEXT = 'Hello! Your OTP is ' + str(otp) + '!'
	print(TEXT)
	msg = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
	server.sendmail('qrotpcode@gmail.com', user_mail,msg)
	server.quit()


def logoutUser(request):
	logout(request)
	return redirect('login')


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

def readQR(request):
	if request.method == 'POST':
		file2 = request.FILES['file']
		fs = FileSystemStorage() 
		filename = fs.save(file2.name, file2)
		
		img = cv2.imread('./qr/media/' + filename)
		detect = cv2.QRCodeDetector()
		value, points, straight_qrcode = detect.detectAndDecode(img)
		user = User.objects.filter(username=user_name)
		global count_qr
		if count_qr == 1:
			if value == str(otp_qr):
				return render(request, 'welcome.html', {'user': user})
			else:
				count_qr += 1
				return render(request, 'readQR.html', {"message": "Invalid OTP"})
    	
		elif count_qr == 2:
			request.method == "POST"
			file2 = request.FILES['file']
			fs = FileSystemStorage() 
			filename = fs.save(file2.name, file2)
			
			img = cv2.imread('./qr/media/' + filename)
			detect = cv2.QRCodeDetector()
			value, points, straight_qrcode = detect.detectAndDecode(img)
			user = User.objects.filter(username=user_name)
			if value == str(otp_qr):
				return render(request, 'welcome.html', {'user': user})
			else:
				count_qr += 1
				return render(request, 'readQR.html')
		else: 
			# count_qr = 1
			# return render(request, 'login.html')
			logout(request)
			# /return render(request, 'login.html')
			return redirect('login')

	return render(request, 'welcome.html')
    	