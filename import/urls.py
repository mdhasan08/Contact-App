from django.urls import path
from . import views

urlpatterns = [
    # api
    path('contact_import_api/', views.ImportContactApi.as_view()),
]

