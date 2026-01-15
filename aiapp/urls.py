from django.urls import path
from .views import generate_page, FashionGenerateAPI, DownloadGeneratedImagesAPI

urlpatterns = [
    path("", generate_page, name="generate-page"),
    path("generate/", FashionGenerateAPI.as_view(), name="fashion-generate"),
    path("download-photos/", DownloadGeneratedImagesAPI.as_view(), name="fashion-generate-api"),
]
