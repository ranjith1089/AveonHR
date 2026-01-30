from django.urls import path

from .views import (
    download_file,
    experience_certificate,
    landing,
    offer_letter,
    preview_pdf,
    travel_expense,
    upload_payslips,
)

urlpatterns = [
    path("", landing, name="landing"),
    path("offer-letter/", offer_letter, name="offer_letter"),
    path("experience-certificate/", experience_certificate, name="experience_certificate"),
    path("travel-expense/", travel_expense, name="travel_expense"),
    path("payslip/", upload_payslips, name="upload_payslips"),
    path("preview/<str:token>/", preview_pdf, name="preview_pdf"),
    path("download/<str:token>/", download_file, name="download_file"),
]

