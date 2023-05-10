from django.urls import path
from .views import *

urlpatterns = [
    path('', convert_docx_into_pdf, name='convert_docx_into_pdf'),
    path('download/<str:filename>/', serve_pdf, name='serve_pdf')
]
