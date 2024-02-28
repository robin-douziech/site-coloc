from django.urls import path
from . import views

app_name = "png_creator"
urlpatterns = [
    path('', views.index, name="index"),
    path('download-result', views.download_result, name="download-result"),
]