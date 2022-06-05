from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils import json
from .models import AppUser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
import secrets
from threading import Thread
from contact_list.settings import ALLOWED_HOSTS
# for send mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create your views here.
def sign_up(request):
    return render(request, 'sign_up.html')

def verification(request, email, otp):
    return render(request, 'verification.html')

def sign_in(request):
    return render(request, 'sign_in.html')


def sign_out(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('access')
    response.delete_cookie('user_name')
    return response


# APIs

def send_email(to, subject, body):
    smtp_server='smtp.gmail.com'
    smtp_port='465'
    sender_email='projecttestmail8@gmail.com'
    sender_password='projectTesting'
    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to
        msg['Subject'] = subject


        html = """\
        <html>
            <head></head>
            <body>
        """
        html += body
        """
            </body>
        </html>
        """
        msg.attach(MIMEText(html,'html'))
        server.sendmail(
            from_addr=sender_email,
            to_addrs=to,
            msg = msg.as_string())
        print("Mail Send")
    except Exception as ex:
        print(str(ex))
    finally:
        if server != None:
            server.quit()

def send_email_thread(to, subject, body):
    thread = Thread(target=send_email,args=(to, subject, body))
    thread.start()

class UserSignUp(CreateAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        result = {}
        try:
            data = request.data
            # data = json.loads(request.body)

            if 'full_name' not in data or data['full_name'] == '':
                return Response("Full name can not be null.")
            if 'email' not in data or data['email'] == '':
                return Response("Email can not be null.")
            if 'password' not in data or data['password'] == '':
                return Response("Password can not be null.")

            username = data['email'].split('@')
            user = User.objects.filter(username=username[0]).first()

            if not user:
                user = User()
                user.username = username[0]

                name = data['full_name'].split(' ')
                user.first_name = name[0]
                if len(name) > 1:
                    name.remove(name[0])
                    name = ' '.join(name)
                    user.last_name = name

                user.email = data['email']
                user.password = make_password(data['password'])
                user.is_active = False

                otp = secrets.token_hex(25)

                app_user = AppUser()
                app_user.user = user
                app_user.full_name = data['full_name']
                app_user.email = data['email']
                app_user.otp = otp

                user.save()
                app_user.save()

                # server_root = "https://" + ALLOWED_HOSTS[1] + "/registration/verification/"
                server_root = "https://" + ALLOWED_HOSTS[1] + "/registration/verification/"
                activation_link = server_root + data['email'] + "/" + otp + "/"

                send_email_thread(data['email'], "Verification for Sign Up", "To confirm your mail and activate your account please click in this LINK : " + activation_link)

                result['message'] = "Success"
                result['status'] = status.HTTP_200_OK
                return Response(result)

            else:
                if user.is_active:
                    result['message'] = "An Account Exists with this Email !"
                    result['status'] = status.HTTP_208_ALREADY_REPORTED
                    return Response(result)
                else:
                    # print("hehe account found")
                    # print(user.email)
                    result['message'] = "Un Active Account Found !"
                    result['email'] = user.email
                    result['status'] = status.HTTP_401_UNAUTHORIZED
                    return Response(result)

        except Exception as ex:
            result['message'] = str(ex)
            result['status'] = status.HTTP_400_BAD_REQUEST
            return Response(result)


class OtpCheck(CreateAPIView):
    permission_classes = []

    def put(self, request):
        try:
            data = json.loads(request.body)

            if 'otp' not in data or data['otp'] == '':
                feedback = {}
                feedback['status'] = status.HTTP_400_BAD_REQUEST
                feedback['message'] = "OTP cant be NULL"
                return Response(feedback)
            if 'otpEmail' not in data or data['otpEmail'] == '':
                feedback = {}
                feedback['status'] = status.HTTP_400_BAD_REQUEST
                feedback['message'] = "Email Lost : Something went wrong"
                return Response(feedback)

            user = User.objects.filter(email=data['otpEmail']).first()

            if not user or user == '':
                feedback = {}
                feedback['status'] = status.HTTP_400_BAD_REQUEST
                feedback['message'] = "No account with this Email !"
                return Response(feedback)

            app_user = AppUser.objects.filter(user=user).first()

            if app_user:
                if app_user.email == data['otpEmail'] and app_user.otp == data['otp']:
                    user.is_active = True
                    app_user.otp = ''

                    user.save()
                    app_user.save()

                    feedback = {}
                    feedback['status'] = status.HTTP_200_OK
                    feedback['message'] = "Account Creation successful"
                    return Response(feedback)

                else:
                    feedback = {}
                    feedback['status'] = status.HTTP_401_UNAUTHORIZED
                    feedback['message'] = "UnAuthorized entry"
                    return Response(feedback)
            else:
                feedback = {}
                feedback['status'] = status.HTTP_400_BAD_REQUEST
                feedback['message'] = "No app user found in this Email !"
                return Response(feedback)


        except Exception as ex:
            feedback = {}
            feedback['status'] = status.HTTP_400_BAD_REQUEST
            feedback['message'] = str(ex)
            return Response(feedback)


class UserSignIn(CreateAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        result = {}
        try:
            data = json.loads(request.body)
            # print(data)
            if 'email' not in data or data['email']=='':
                result['message'] = "Email can not be null."
                result['status'] = status.HTTP_400_BAD_REQUEST
                return Response(result)

            if 'password' not in data or data['password'] == '':
                result['message'] = "Password can not be null."
                result['status'] = status.HTTP_400_BAD_REQUEST
                return Response(result)

            user = User.objects.filter(email=data['email']).first()
            if not user or not user.is_active:
                result = {}
                result['message'] = "Please Create an Account before sign in!"
                result['status'] = status.HTTP_404_NOT_FOUND
                return Response(result)
            else:
                if not check_password(data['password'], user.password):
                    result = {}
                    result['message'] = "Invalid credentials"
                    result['status'] = status.HTTP_401_UNAUTHORIZED
                    return Response(result)
                else:
                    app_user = AppUser.objects.filter(user=user).first()
                    refresh_token = RefreshToken.for_user(user)
                    data = {
                        'user_name': user.username,
                        'slug': app_user.slug,
                        'access': str(refresh_token.access_token),
                        'token': str(refresh_token),
                        'status': status.HTTP_200_OK
                    }
                    return Response(data)
        except Exception as e:
            result = {}
            result['status'] = status.HTTP_400_BAD_REQUEST
            result['message'] = str(e)
            return Response(result)


class SendVerificationLink(CreateAPIView):
    permission_classes = []

    def put(self, request):
        try:
            data = json.loads(request.body)
            if 'email' not in data or data['email'] == '':
                feedback = {}
                feedback['message'] = "Email LOST ! Something Went Wrong"
                feedback['status'] = status.HTTP_400_BAD_REQUEST
                return Response(feedback)

            user = User.objects.filter(email=data['email']).first()
            # print("printing user")
            # print(user)
            otp = secrets.token_hex(25)
            server_root = "https://" + ALLOWED_HOSTS[1] + "/registration/verification/"

            if user:
                app_user = AppUser.objects.filter(email=data['email']).first()
                app_user.otp = otp

                app_user.save()
                activation_link = server_root + data['email'] + "/" + otp + "/"
                send_email_thread(data['email'], "Verification for Sign Up", "To confirm your mail and activate your account please click in this LINK : " + activation_link)

                feedback = {}
                feedback['message'] = "Activation Mail Send !"
                feedback['status'] = status.HTTP_200_OK
                return Response(feedback)
            else:
                feedback = {}
                feedback['message'] = "Invalid request!"
                feedback['status'] = status.HTTP_400_BAD_REQUEST
                return Response(feedback)

        except Exception as ex:
            feedback = {}
            feedback['message'] = str(ex)
            feedback['status'] = status.HTTP_400_BAD_REQUEST
            return Response(feedback)

