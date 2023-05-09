from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', convert_docx_into_pdf, name='convert_docx_into_pdf'),
    path('download/<str:filename>/', serve_pdf, name='serve_pdf')
]
