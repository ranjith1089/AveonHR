from django import forms
from django.core.exceptions import ValidationError

EXECUTABLE_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".sh",
    ".ps1",
    ".vbs",
    ".js",
    ".jar",
    ".msi",
    ".com",
    ".scr",
    ".apk",
    ".app",
    ".bin",
    ".dll",
}

EXCEL_EXTENSIONS = {".xlsx", ".xls"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _extension(filename: str) -> str:
    return ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""


class PayslipUploadForm(forms.Form):
    company_name = forms.CharField(label="Company Name", max_length=200)
    company_address = forms.CharField(
        label="Company Address", widget=forms.Textarea(attrs={"rows": 3})
    )
    company_email = forms.EmailField(label="Company Email", required=False)
    company_phone = forms.CharField(label="Company Phone", required=False, max_length=40)
    company_logo = forms.ImageField(label="Company Logo", required=False)
    salary_file = forms.FileField(label="Salary Statement (Excel)")

    def clean_salary_file(self):
        file = self.cleaned_data.get("salary_file")
        if not file:
            return file
        filename = file.name or ""
        ext = _extension(filename)
        if ext in EXECUTABLE_EXTENSIONS:
            raise ValidationError("Executable files are not allowed.")
        if ext not in EXCEL_EXTENSIONS:
            raise ValidationError("Please upload a valid Excel file (.xlsx or .xls).")
        return file

    def clean_company_logo(self):
        file = self.cleaned_data.get("company_logo")
        if not file:
            return file
        filename = file.name or ""
        ext = _extension(filename)
        if ext in EXECUTABLE_EXTENSIONS:
            raise ValidationError("Executable files are not allowed.")
        if ext not in IMAGE_EXTENSIONS:
            raise ValidationError("Logo must be a PNG or JPG image.")
        return file


class OfferLetterForm(forms.Form):
    OFFER_TYPES = [
        ("internship", "INTERNSHIP OFFER LETTER"),
        ("appointment", "Appointment Order"),
        ("employment_offer", "OFFER LETTER"),
    ]

    offer_type = forms.ChoiceField(label="Offer Letter Type", choices=OFFER_TYPES)
    
    # Internship/Offer Letter fields
    name = forms.CharField(label="Name", max_length=200, required=False)
    roll_number = forms.CharField(label="Roll Number", max_length=100, required=False)
    course = forms.CharField(label="Course", max_length=200, required=False)
    college_name = forms.CharField(label="College Name", max_length=200, required=False)
    college_address = forms.CharField(
        label="College Address", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    internship_role = forms.CharField(label="Internship Role", max_length=200, required=False)
    start_date = forms.DateField(
        label="Start Date", widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    
    # Appointment Order fields
    serial_no = forms.CharField(label="Ref No", max_length=100, required=False)
    employee_name = forms.CharField(label="Employee Name", max_length=200, required=False)
    present_address1 = forms.CharField(label="Address Line 1", max_length=200, required=False)
    present_address2 = forms.CharField(label="Address Line 2", max_length=200, required=False)
    present_address3 = forms.CharField(label="Address Line 3", max_length=200, required=False)
    present_address_city = forms.CharField(label="City", max_length=100, required=False)
    present_address_state = forms.CharField(label="State", max_length=100, required=False)
    present_address_pin = forms.CharField(label="PIN Code", max_length=20, required=False)
    designation = forms.CharField(label="Designation", max_length=200, required=False)
    join_date = forms.DateField(
        label="Joining Date", widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    probation_period = forms.CharField(label="Probation Period (days)", max_length=50, required=False)
    ctc = forms.CharField(label="CTC (in words)", max_length=500, required=False)
    company_name = forms.CharField(label="Company Name", max_length=200, required=False)
    signatory = forms.CharField(label="Signatory Name", max_length=200, required=False)
    signatory_designation = forms.CharField(label="Signatory Designation", max_length=200, required=False)
    
    # Employment Offer Letter fields
    candidate_name = forms.CharField(label="Candidate Name", max_length=200, required=False)
    position = forms.CharField(label="Position", max_length=200, required=False)
    annual_ctc = forms.DecimalField(label="Annual CTC (Rs.)", max_digits=12, decimal_places=2, required=False)
    ctc_in_words = forms.CharField(label="CTC in Words", max_length=500, required=False)
    joining_date = forms.DateField(
        label="Joining Date", widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    employer_name = forms.CharField(label="Employer Name", max_length=200, required=False)
    employer_designation = forms.CharField(label="Employer Designation", max_length=200, required=False)
    
    # Compensation breakdown
    basic_monthly = forms.DecimalField(label="Basic (Monthly)", max_digits=12, decimal_places=2, required=False)
    basic_annual = forms.DecimalField(label="Basic (Annual)", max_digits=12, decimal_places=2, required=False)
    da_monthly = forms.DecimalField(label="DA (Monthly)", max_digits=12, decimal_places=2, required=False)
    da_annual = forms.DecimalField(label="DA (Annual)", max_digits=12, decimal_places=2, required=False)
    hra_monthly = forms.DecimalField(label="HRA (Monthly)", max_digits=12, decimal_places=2, required=False)
    hra_annual = forms.DecimalField(label="HRA (Annual)", max_digits=12, decimal_places=2, required=False)
    ta_monthly = forms.DecimalField(label="TA (Monthly)", max_digits=12, decimal_places=2, required=False)
    ta_annual = forms.DecimalField(label="TA (Annual)", max_digits=12, decimal_places=2, required=False)
    food_allowance_monthly = forms.DecimalField(label="Food Allowance (Monthly)", max_digits=12, decimal_places=2, required=False)
    food_allowance_annual = forms.DecimalField(label="Food Allowance (Annual)", max_digits=12, decimal_places=2, required=False)
    pf_employee_monthly = forms.DecimalField(label="PF Employee (Monthly)", max_digits=12, decimal_places=2, required=False)
    pf_employee_annual = forms.DecimalField(label="PF Employee (Annual)", max_digits=12, decimal_places=2, required=False)
    pf_employer_monthly = forms.DecimalField(label="PF Employer (Monthly)", max_digits=12, decimal_places=2, required=False)
    pf_employer_annual = forms.DecimalField(label="PF Employer (Annual)", max_digits=12, decimal_places=2, required=False)


class ExperienceCertificateForm(forms.Form):
    TITLE_CHOICES = [
        ("Mr.", "Mr."),
        ("Ms.", "Ms."),
        ("Mrs.", "Mrs."),
    ]
    
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    
    title = forms.ChoiceField(label="Title", choices=TITLE_CHOICES)
    employee_name_exp = forms.CharField(label="Employee Name", max_length=200)
    employee_no = forms.CharField(label="Employee ID", max_length=100)
    company_name_exp = forms.CharField(label="Company Name", max_length=200)
    join_date_exp = forms.DateField(
        label="Joining Date", widget=forms.DateInput(attrs={"type": "date"})
    )
    leaving_date = forms.DateField(
        label="Leaving Date", widget=forms.DateInput(attrs={"type": "date"})
    )
    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES)
    designation_exp = forms.CharField(label="Designation", max_length=200)
    signatory_exp = forms.CharField(label="Signatory Name", max_length=200)
    signatory_designation_exp = forms.CharField(label="Signatory Designation", max_length=200)


class TravelExpenseForm(forms.Form):
    # Company Information
    company_name_travel = forms.CharField(label="Company Name", max_length=200)
    company_address_travel = forms.CharField(label="Company Address", max_length=300)
    company_city_state = forms.CharField(label="City, State, ZIP", max_length=200)
    company_country = forms.CharField(label="Country", max_length=100, initial="India")
    
    # Report Information
    report_title = forms.CharField(label="Report Title", max_length=200)
    business_purpose = forms.CharField(
        label="Business Purpose",
        widget=forms.Textarea(attrs={"rows": 3}),
        max_length=500
    )
    submitted_by = forms.CharField(label="Submitted By", max_length=200)
    submitted_on = forms.DateField(
        label="Submitted On", widget=forms.DateInput(attrs={"type": "date"})
    )
    report_to = forms.CharField(label="Report To", max_length=200)
    reporting_period_start = forms.DateField(
        label="Reporting Period Start", widget=forms.DateInput(attrs={"type": "date"})
    )
    reporting_period_end = forms.DateField(
        label="Reporting Period End", widget=forms.DateInput(attrs={"type": "date"})
    )
    
    # Currency
    report_currency = forms.CharField(label="Report Currency", max_length=10, initial="INR")
    
    # Expense Data (JSON format - will be populated via JavaScript)
    expense_data = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "placeholder": "Expense data in JSON format"}),
        required=False
    )

