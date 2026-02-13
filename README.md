# Aveon HR Suite

Aveon HR Suite is a Django-based document automation application by **Aveon Infotech Private Limited**. It helps HR and admin teams generate professional, printable documents and reports with a web interface.

## Features

- Offer Letter Generator
  - Internship Offer Letter
  - Appointment Order
  - Employment Offer Letter
- Experience Certificate Generator
- Payslip Generator (Excel upload → PDF/ZIP output)
- Travel Expense Report Generator
- CMS Proposal Quotation Generator (plain-text institutional ERP proposal)

## Tech Stack

- Python 3
- Django 4.2
- ReportLab (PDF generation)
- Pandas + OpenPyXL (Excel parsing)
- Pillow (image handling)

## Project Structure

```text
AveonHR/
├── manage.py
├── requirements.txt
├── payslip_project/          # Django project settings and root URLs
├── payslip/                  # Main app (forms, views, services, templates, static)
├── db.sqlite3
└── PYTHONANYWHERE_DEPLOYMENT.md
```

## Setup Instructions

### 1) Clone and enter project

```bash
git clone <your-repo-url>
cd AveonHR
```

### 2) Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run migrations

```bash
python manage.py migrate
```

### 5) Start server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Main Routes

- `/` → Landing page
- `/offer-letter/` → Offer letter generator
- `/experience-certificate/` → Experience certificate generator
- `/payslip/` → Payslip upload and generation
- `/travel-expense/` → Travel expense report generator
- `/proposal-quotation/` → CMS proposal quotation generator

## Testing & Validation

Run tests:

```bash
python manage.py test
```

Run Django checks:

```bash
python manage.py check
```

## Output Behavior

- Most modules generate downloadable PDF files.
- Payslip module can generate a ZIP containing multiple payslips.
- Proposal quotation module outputs a professional plain-text proposal suitable for Word/PDF conversion.

## Deployment

For PythonAnywhere deployment steps, refer to:

- `PYTHONANYWHERE_DEPLOYMENT.md`

## Company

Developed and maintained by **Aveon Infotech Private Limited**.
