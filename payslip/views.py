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
    ProposalQuotationForm,
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





def _build_cms_proposal_text(client_name: str, client_location: str, institution_type: str) -> str:
    return f"""1. COVER PAGE

Proposal Title: Comprehensive ERP Proposal – Aveon College Management System (CMS) ERP
Prepared By: Aveon Infotech Private Limited
Client Name: {client_name}
Client Location: {client_location}
Institution Type: {institution_type}
Date: [DD/MM/YYYY]
Placeholders: [Aveon Logo] [Client Logo]

2. SUBJECT & INTRODUCTION

Subject: Proposal for Supply, Implementation, Training, and Support of Aveon College Management System (CMS) ERP

Respected Sir/Madam,

Greetings from Aveon Infotech Private Limited.

We are pleased to submit this comprehensive proposal for implementation of Aveon College Management System (CMS) ERP for {client_name}, {client_location}. This proposal is prepared for consideration by the College Management, Principal, IQAC, and Purchase Committee, with specific alignment to statutory, accreditation, and institutional governance requirements in Indian higher education.

Our proposed platform is designed to digitize and integrate end-to-end institutional operations across admissions, academics, examination, administration, finance, compliance, and student services through a secure and scalable ERP ecosystem.

3. PROJECT OVERVIEW

Aveon CMS ERP is an integrated institutional platform that automates admission, academics, examination, finance, HR, hostel, library, and compliance workflows in a single system. The solution is aligned to CBCS, OBE, NAAC, NIRF, and IQAC requirements, and supports autonomous as well as affiliated colleges. With configurable role-based access, dashboards, analytics, and mobile-first communication, it ensures operational efficiency, statutory readiness, and transparent governance for higher education institutions.

4. ABOUT AVEON INFOTECH

Company Name: Aveon Infotech Private Limited
Established: 2012

Core Domain Expertise:
- College ERP solutions
- School ERP solutions
- Controller of Examination (COE) automation
- NAAC, NIRF, and IQAC support systems
- Hostel and library management
- Payroll and finance management
- Institutional custom software development

Institutional Delivery Strengths:
- Deep process knowledge of Indian higher-education regulations
- Experience in implementing modules for autonomous and affiliated institutions
- Academic workflow understanding across UG, PG, and professional programs
- Governance-focused implementation approach suitable for purchase committees

5. SCOPE OF WORK / PROJECT DETAILS

5.1 Admission & Student Lifecycle
- Online admission enquiry, registration, and application workflows
- Merit list generation and configurable admission rounds
- Document verification and digital admission file
- Fee challan generation and receipt tracking
- Student profile with lifecycle coverage from admission to alumni
- Certificate and document issue tracking

5.2 Academic Management (CBCS, OBE, Open Electives)
- Academic calendar setup and timetable management
- Program, batch, semester, and section configuration
- CBCS-based curriculum mapping and credit tracking
- Open elective basket creation and student choice allocation
- OBE framework support: CO-PO-PSO mapping and attainment analytics
- Attendance, internal marks, assignment, and tutorial workflows

5.3 Learning Management System (LMS)
- Course-wise content repository and faculty upload
- Lesson plan tracking and session planning
- Assignment publishing, submission, and evaluation
- Discussion forum and academic announcement board
- Continuous learning records for academic audit readiness

5.4 Controller of Examination (COE)
- Examination timetable planning and hall allocation
- Examination application and fee processing
- Question paper workflow and secure exam coordination
- Internal/external mark entry with moderation controls
- Grade processing, SGPA/CGPA calculation, and publication
- Revaluation, arrear, supplementary, and result history management

5.5 Finance, Fees & Accounts
- Configurable fee heads, concessions, and installment structures
- Student fee collection through online/offline modes
- Receipt, ledger, and outstanding management
- Institutional accounting workflows (income/expense/cash-bank)
- Finance dashboards for management decision support
- GST-ready reporting framework where applicable

5.6 HR & Payroll
- Employee master with service records
- Attendance, leave, and holiday management
- Payroll setup with earnings, deductions, and compliance components
- Payslip generation and salary register reports
- HR letters and service certificate workflows

5.7 Library, Hostel, Transport, Inventory
- Library accessioning, issue/return, and fine tracking
- Hostel room allocation, occupancy, and mess billing support
- Transport route, stage, and student pass management
- Inventory purchase request, stock issue, and asset tracking

5.8 NAAC / NIRF / IQAC Modules
- NAAC criteria-wise data capture and evidence mapping
- NIRF data templates and annual comparative analytics
- IQAC action plan tracking and AQAR support data extraction
- Department-wise KPI and compliance-ready reporting

5.9 Mobile Apps & Communication (SMS, WhatsApp, Email)
- Mobile application access for students, faculty, and parents (as applicable)
- Push notifications for attendance, fees, exam, and circulars
- Integrated SMS/WhatsApp/Email communication workflow
- Role-based alert subscriptions and message log audit

6. IMPLEMENTATION METHODOLOGY (PHASE-WISE)

Phase 1: Discovery and Requirement Sign-off
- Stakeholder workshops with Management, Principal, IQAC, COE, Accounts, and Departments
- As-is process study and gap analysis
- Finalization of scope and configuration blueprint

Phase 2: System Configuration and Master Setup
- Academic structure, users, role matrix, and module parameterization
- Approval hierarchies and workflow setup
- Template and report configuration

Phase 3: Data Preparation and Migration
- Client submission of validated legacy data in agreed templates
- Data quality checks and controlled import cycles
- Reconciliation and sign-off for migrated records

Phase 4: Training and User Acceptance Testing (UAT)
- Role-based training for administrators, faculty, and non-teaching staff
- UAT execution against agreed scenarios
- Issue tracking, closure, and acceptance confirmation

Phase 5: Go-Live and Stabilization
- Module-wise production rollout
- Hypercare support during stabilization period
- Post go-live review and optimization recommendations

7. PROJECT TIMELINE WITH MILESTONES

Indicative Duration: 12 to 16 weeks from date of work order and receipt of initial payment

Milestones:
- Week 1-2: Requirement study and scope freeze
- Week 3-5: System configuration and workflow setup
- Week 6-8: Data migration cycle and validation
- Week 9-11: Training and UAT sign-off
- Week 12-16: Go-live and stabilization

Delay Disclaimer:
- Timeline is subject to timely client-side approvals, data submission, and nodal coordination.
- Any delay in feedback, incomplete data, change requests beyond signed scope, or postponement of training schedules shall proportionately extend delivery timelines without penalty to Aveon Infotech Private Limited.

8. PROJECT INVESTMENT

8.1 Commercial Model (Indicative)
- Per Student Pricing (Annual SaaS License): INR 850 per student per academic year
- Minimum Billing Commitment: 1,000 students
- One-Time Implementation Charges: INR 3,50,000
- Applicable GST: 18% extra on all commercial values

8.2 Illustration (for 1,000 students)
- Annual License: INR 8,50,000
- Implementation: INR 3,50,000
- Subtotal: INR 12,00,000
- GST @18%: INR 2,16,000
- Total (Year 1): INR 14,16,000

8.3 Payment Milestones
- 40% of implementation + 100% first-year license: Along with work order / PO release
- 40% of implementation: On completion of configuration and data migration stage
- 20% of implementation: On go-live and UAT sign-off
- Renewal license (from Year 2 onwards): Payable in advance before start of academic year

9. SUPPORT & MAINTENANCE MODEL

Support Coverage:
- Helpdesk support through ticketing/email/phone during business hours
- Priority-based issue response and resolution tracking
- Functional assistance for configured workflows
- Minor version updates and performance improvements

Review and Governance:
- Periodic review meetings with designated institutional coordinators
- Support MIS and closure reports
- Optional annual health-check and optimization advisory

10. DETAILED TERMS & CONDITIONS

10.1 Commercial & GST
- All prices are in Indian Rupees (INR).
- GST shall be charged extra at 18% as applicable under law.
- Statutory changes in taxation, if any, shall be additionally applicable.

10.2 Payment Terms
- Payments are due as per agreed milestone schedule.
- Delayed payments may attract service suspension and applicable delay charges after written notice.
- Purchase order/work order must clearly mention scope, commercials, and tax details.

10.3 Scope & Customization
- Proposal scope is limited to modules and features explicitly specified herein.
- Additional features, custom reports, integrations, or process changes not in signed scope shall be treated as change requests and commercially evaluated separately.

10.4 Data Migration Responsibility
- Client shall provide accurate, complete, and validated data in prescribed templates.
- Aveon shall perform migration based on submitted data; data correctness remains client responsibility.
- Rework due to inaccurate/incomplete data shall be handled as additional effort.

10.5 Implementation Sign-off
- Module completion shall be deemed accepted upon UAT sign-off by authorized client representative.
- If sign-off is delayed beyond 10 working days after successful demonstration/UAT closure without documented critical defects, milestone acceptance shall be considered deemed sign-off.

10.6 Training
- Role-based training sessions are included as per agreed implementation plan.
- Additional training batches, refresher programs, or off-schedule sessions may be chargeable.

10.7 Third-Party Integrations
- SMS, WhatsApp, payment gateway, biometric, and other third-party services require active subscriptions/licenses from respective providers.
- Third-party downtime, API policy changes, or vendor service limitations are outside Aveon liability.

10.8 Hosting & Security
- Hosting may be cloud/on-premise as mutually agreed.
- Client shall ensure required infrastructure readiness for on-premise deployments.
- Aveon follows reasonable industry-standard controls for access, backup, and application security within agreed hosting model.

10.9 Intellectual Property
- Pre-existing platform IP, source framework, templates, and reusable components remain sole property of Aveon Infotech Private Limited.
- Client receives usage rights for subscribed term and agreed scope.

10.10 Confidentiality
- Both parties shall maintain confidentiality of non-public business, academic, technical, and student data shared during engagement.
- Confidential information shall not be disclosed to third parties except as required by law.

10.11 Limitation of Liability
- Aveon’s aggregate liability under this engagement shall be limited to fees received by Aveon for the affected service period, excluding indirect, incidental, consequential, or punitive damages.

10.12 Termination
- Either party may terminate for material breach upon written notice and cure period of 30 days.
- Fees for services rendered up to termination date remain payable.
- Data handover/support at exit shall be provided as per agreed disengagement terms.

10.13 Governing Law & Jurisdiction
- This proposal and resulting contract shall be governed by the laws of India.
- Courts at Coimbatore, Tamil Nadu shall have exclusive jurisdiction.

11. WHY PARTNER WITH AVEON INFOTECH

- Proven institutional ERP capability since 2012
- Domain-led understanding of NAAC, NIRF, IQAC, CBCS, and OBE
- Structured implementation suitable for governing bodies and purchase committees
- Strong blend of academic, administrative, and compliance automation
- Scalable, secure, and support-oriented delivery model
- Long-term partnership approach focused on measurable institutional outcomes

12. AUTHORIZATION & SIGNATURE

For Aveon Infotech Private Limited

Authorized Signatory:
Parvathi G
Chief Executive Officer (CEO)

Date: ____________________
Place: ___________________

Acknowledgement by Client:

Name: ____________________
Designation: ______________
Institution Seal & Signature: ____________________
Date: _____________________
"""
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





def _as_text_download_response(content: str, filename: str = "aveon_cms_erp_proposal.txt") -> HttpResponse:
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Cache-Control"] = "no-store"
    return response

def proposal_quotation(request: HttpRequest) -> HttpResponse:
    context = {"form": ProposalQuotationForm()}
    if request.method != "POST":
        return render(request, "payslip/proposal_quotation.html", context)

    form = ProposalQuotationForm(request.POST)
    if not form.is_valid():
        context["form"] = form
        return render(request, "payslip/proposal_quotation.html", context)

    proposal_text = _build_cms_proposal_text(
        form.cleaned_data["client_name"],
        form.cleaned_data["client_location"],
        form.cleaned_data["institution_type"],
    )

    if request.POST.get("action") == "download":
        return _as_text_download_response(proposal_text)

    context["form"] = form
    context["proposal_text"] = proposal_text
    return render(request, "payslip/proposal_quotation.html", context)
