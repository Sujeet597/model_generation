from django.urls import path
from .views import generate_page,history_page, FashionGenerateAPI, DownloadGeneratedImagesAPI, GenerationHistoryAPI

urlpatterns = [
    path("", generate_page, name="generate-page"),
    path("history/", history_page, name="generation-history-page"),
    path("generate/", FashionGenerateAPI.as_view(), name="fashion-generate"),
    path("download-photos/", DownloadGeneratedImagesAPI.as_view(), name="fashion-generate-api"),
    path("generation-history/", GenerationHistoryAPI.as_view(), name="generation-history"),
]
