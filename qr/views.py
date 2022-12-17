from multiprocessing import context
from django.shortcuts import render
import random
import smtplib
import qrcode
import bcrypt
import glob
import cv2
import pandas as pd
import pathlib
import hashlib
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
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

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib

import cv2
import pyzbar.pyzbar as pyzbar
from django.http import StreamingHttpResponse

totp = pyotp.TOTP('base32secret3232', interval = 60)
otp_qr = 0
otp_mail = 0
# login gmail server
def gmail_login(username, password):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.connect("smtp.gmail.com", 587)
    server.starttls()
    server.login(username, password)
    return server


def welcome(request):
	return render(request, 'welcome.html')

# not used
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
		if totp.verify(user_otp):
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
		request.POST._mutable = True
		password = request.POST.get('password1')
		# password = password.encode('utf-8')
		# hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt(10))
		hashedPassword = hashlib.md5(password.encode()).hexdigest()
		request.POST['password1'] = hashedPassword
		request.POST['password2'] = hashedPassword
		print(request.POST['password1'])
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			# messages.success(request, 'Account was created for ' + user)
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
		passw = request.POST.get('password')
		hashedPassword = hashlib.md5(passw.encode()).hexdigest()
		# print(type(passw))
		# hashedPassword = bcrypt.hashpw(passw, bcrypt.gensalt(10))
		# password = hashedPassword
		# print(type(password))
		user = authenticate(request, username=username, password=hashedPassword)
		# user = User.objects.get(username=username)
		# ps = user.password.encode('utf-8')
		# print(bcrypt.checkpw(passw, ps))
		# if bcrypt.checkpw(passw, user.password):
  		# 	print("login success")
		
		if user is not None:
				login(request, user)
				msg = MIMEMultipart()
				msg['Subject'] = "QR Code"
				msg['From'] = "otpandqrcode@gmail.com"
				msg['To'] = "tramngo0381@gmail.com"

				# make qr code
				name = ''.join([str(random.randint(0,9)) for i in range(6)])
				randnum = random.randint(000000,999999)
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

				server = gmail_login("otpandqrcode@gmail.com", 'yzmwvnqqwnbuyfjq')
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
	server.login('tramngo504@gmail.com', 'fizdaofigoenqnve')
	# otp = ''.join([str(random.randint(0,9)) for i in range(4)])
	# totp = pyotp.TOTP('base32secret3232', interval = 60)
	global otp_mail, totp
	otp = totp.now()
	otp_mail = otp
	msg = 'Hello! Your OTP is ' + str(otp)
	server.sendmail('tramngo504@gmail.com', 'tramngo0381@gmail.com',msg)
	server.quit()


def logoutUser(request):
	logout(request)
	return redirect('login')


def stream(request):
   
	cap = cv2.VideoCapture(0)
	font = cv2.FONT_HERSHEY_PLAIN
	check = False
	otp = ""
	while  True:
		_, frame = cap.read()

		decodedObjects = pyzbar.decode(frame)
		for obj in decodedObjects:
			# print("Data", obj.data)
			otp = (obj.data).decode("utf-8")
			print ("OTP: ", otp)
			if type(otp) is str:
				check = True
				break
		# cv2.imshow ("Frame", frame)
		cv2.imwrite('demo.jpg', frame)
		yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')
		# key = cv2.waitKey(1)
		if check:
			print(otp)
			print(otp_qr)
			break
	if otp == str(otp_qr):
		print("True")
		return render(request, 'welcome.html')
		# return redirect('welcome.html')
	return render(request, 'login.html')

def video_feed(request):
    return StreamingHttpResponse(stream(request), content_type='multipart/x-mixed-replace; boundary=frame')

def read_qr_code(filename):
    """Read an image and read the QR code.
    
    Args:
        filename (string): Path to file
    
    Returns:
        qr (string): Value from QR code
    """
    
    try:
        img = cv2.imread(filename)
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(img)
        return value
    except:
        return
def readQR(request):
	if request.method == 'POST':
		file2 = request.FILES['file']
		fs = FileSystemStorage() 
		filename = fs.save(file2.name, file2)
		print(filename)
		img = cv2.imread('./qr/media/' + filename)
		detect = cv2.QRCodeDetector()
		value, points, straight_qrcode = detect.detectAndDecode(img)
		print(value)
		if value == str(otp_qr):
			return render(request, 'welcome.html')
		else:
			return render(request, "login.html", {"message": "Invalid OTP"})
    	# if value == str(otp_qr):
        # 	return render(request, 'welcome.html')
    	# else:
        # 	return render(request, "login.html", {"message": "Invalid OTP"})
        # detect = cv2.QRCodeDetector()
        # value, points, straight_qrcode = detect.detectAndDecode(img)
		#defaults to   MEDIA_ROOT  
        # filename = fs.save(file2.name, file2)
		# output = pyzbar.decode(file2)
		# print(output)
		# detect = cv2.QRCodeDetector()
		# value, points, straight_qrcode = detect.detectAndDecode(file2)
		# print(value)
	return render(request, 'welcome.html')
    	