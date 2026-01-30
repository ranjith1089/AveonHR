from __future__ import annotations

import uuid

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_GET

from .forms import (
    ExperienceCertificateForm,
    OfferLetterForm,
    PayslipUploadForm,
    TravelExpenseForm,
)
from .services.payslip_service import generate_payslips
from .utils import (
    CompanyInfo,
    build_appointment_order_pdf,
    build_employment_offer_pdf,
    build_experience_certificate_pdf,
    build_offer_letter_pdf,
    build_travel_expense_pdf,
)

_FILE_CACHE: dict[str, tuple[bytes, str, str]] = {}


def _save_content(content: bytes | str, content_type: str, filename: str) -> str:
    token = uuid.uuid4().hex
    if isinstance(content, str):
        stored = content.encode("utf-8")
    else:
        stored = bytes(content)
    _FILE_CACHE[token] = (stored, content_type, filename)
    return token


def _get_content(token: str) -> tuple[bytes, str, str] | None:
    return _FILE_CACHE.get(token)


def upload_payslips(request: HttpRequest) -> HttpResponse:
    context = {"form": PayslipUploadForm()}
    if request.method != "POST":
        return render(request, "payslip/upload.html", context)

    form = PayslipUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        context["form"] = form
        return render(request, "payslip/upload.html", context)

    company = CompanyInfo(
        name=form.cleaned_data["company_name"],
        address=form.cleaned_data["company_address"],
        email=form.cleaned_data.get("company_email"),
        phone=form.cleaned_data.get("company_phone"),
    )
    logo = form.cleaned_data.get("company_logo")
    logo_bytes = logo.read() if logo else None

    salary_file = form.cleaned_data["salary_file"]
    try:
        result = generate_payslips(salary_file.read(), company, logo_bytes)
    except ValueError as exc:
        context["form"] = form
        context["error"] = str(exc)
        return render(request, "payslip/upload.html", context)

    preview_token = _save_content(result.preview_content, "application/pdf", result.preview_filename)
    download_token = _save_content(result.content, result.content_type, result.filename)

    download_label = "Download PDF" if result.content_type == "application/pdf" else "Download ZIP"
    download_filename = result.filename

    context["preview_url"] = reverse("preview_pdf", kwargs={"token": preview_token})
    context["download_url"] = reverse("download_file", kwargs={"token": download_token})
    context["download_label"] = download_label
    context["download_filename"] = download_filename
    return render(request, "payslip/preview.html", context)


def landing(request: HttpRequest) -> HttpResponse:
    return render(request, "payslip/landing.html")


def offer_letter(request: HttpRequest) -> HttpResponse:
    context = {"form": OfferLetterForm()}
    if request.method != "POST":
        return render(request, "payslip/offer_letter.html", context)

    form = OfferLetterForm(request.POST)
    if not form.is_valid():
        context["form"] = form
        return render(request, "payslip/offer_letter.html", context)

    context["form"] = form
    context["data"] = form.cleaned_data
    context["offer_type_label"] = dict(form.fields["offer_type"].choices).get(
        form.cleaned_data["offer_type"], form.cleaned_data["offer_type"]
    )
    pdf_data = dict(form.cleaned_data)
    pdf_data["offer_type_label"] = context["offer_type_label"]
    
    # Generate PDF based on letter type
    offer_type = form.cleaned_data.get("offer_type")
    if offer_type == "appointment":
        pdf_bytes = build_appointment_order_pdf(pdf_data)
        filename = "appointment_order.pdf"
    elif offer_type == "employment_offer":
        pdf_bytes = build_employment_offer_pdf(pdf_data)
        filename = "employment_offer.pdf"
    else:
        pdf_bytes = build_offer_letter_pdf(pdf_data)
        filename = "offer_letter.pdf"
    
    preview_token = _save_content(pdf_bytes, "application/pdf", filename)
    download_token = _save_content(pdf_bytes, "application/pdf", filename)
    context["preview_url"] = reverse("preview_pdf", kwargs={"token": preview_token})
    context["download_url"] = reverse("download_file", kwargs={"token": download_token})
    context["download_label"] = "Download PDF"
    context["download_filename"] = filename
    return render(request, "payslip/offer_letter.html", context)


@require_GET
@xframe_options_exempt
def preview_pdf(request: HttpRequest, token: str) -> HttpResponse:
    stored = _get_content(token)
    if not stored:
        return HttpResponse("PDF not found.", status=404)
    content, content_type, filename = stored
    if content_type != "application/pdf":
        return HttpResponse("Preview is not a PDF.", status=500)
    if not content.startswith(b"%PDF-"):
        snippet = repr(content[:12])
        return HttpResponse(f"Invalid PDF content. Starts with {snippet}.", status=500)
    response = HttpResponse(content, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    response["Content-Length"] = str(len(content))
    response["Cache-Control"] = "no-store"
    return response


@require_GET
def download_file(request: HttpRequest, token: str) -> HttpResponse:
    stored = _get_content(token)
    if not stored:
        return HttpResponse("File not found.", status=404)
    content, content_type, filename = stored
    if content_type == "application/pdf" and not content.startswith(b"%PDF-"):
        return HttpResponse("Invalid PDF content.", status=500)
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Content-Length"] = str(len(content))
    response["Cache-Control"] = "no-store"
    return response


def experience_certificate(request: HttpRequest) -> HttpResponse:
    context = {"form": ExperienceCertificateForm()}
    if request.method != "POST":
        return render(request, "payslip/experience_certificate.html", context)

    form = ExperienceCertificateForm(request.POST)
    if not form.is_valid():
        context["form"] = form
        return render(request, "payslip/experience_certificate.html", context)

    context["form"] = form
    context["data"] = form.cleaned_data

    pdf_bytes = build_experience_certificate_pdf(form.cleaned_data)
    filename = "experience_certificate.pdf"

    preview_token = _save_content(pdf_bytes, "application/pdf", filename)
    download_token = _save_content(pdf_bytes, "application/pdf", filename)
    context["preview_url"] = reverse("preview_pdf", kwargs={"token": preview_token})
    context["download_url"] = reverse("download_file", kwargs={"token": download_token})
    context["download_label"] = "Download PDF"
    context["download_filename"] = filename
    return render(request, "payslip/experience_certificate.html", context)


def travel_expense(request: HttpRequest) -> HttpResponse:
    context = {"form": TravelExpenseForm()}
    if request.method != "POST":
        return render(request, "payslip/travel_expense.html", context)

    form = TravelExpenseForm(request.POST)
    if not form.is_valid():
        context["form"] = form
        return render(request, "payslip/travel_expense.html", context)

    context["form"] = form
    context["data"] = form.cleaned_data

    pdf_bytes = build_travel_expense_pdf(form.cleaned_data)
    filename = "travel_expense_report.pdf"

    preview_token = _save_content(pdf_bytes, "application/pdf", filename)
    download_token = _save_content(pdf_bytes, "application/pdf", filename)
    context["preview_url"] = reverse("preview_pdf", kwargs={"token": preview_token})
    context["download_url"] = reverse("download_file", kwargs={"token": download_token})
    context["download_label"] = "Download PDF"
    context["download_filename"] = filename
    return render(request, "payslip/travel_expense.html", context)

