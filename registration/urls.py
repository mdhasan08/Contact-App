from django.urls import path
from . import views

urlpatterns = [
    # API urls
    path('api/sign_up/', views.UserSignUp.as_view()),
    path('otp_check_api/', views.OtpCheck.as_view()),
    path('api/sign_in/', views.UserSignIn.as_view()),
    path('send_verification_link_api/', views.SendVerificationLink.as_view()),

    # function based views
    path('signup/', views.sign_up),
    path('verification/<str:email>/<str:otp>/', views.verification),
    path('signin/', views.sign_in),
    path('signout/', views.sign_out),
]
