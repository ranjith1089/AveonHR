from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..utils import CompanyInfo, build_payslip_pdf, build_zip, parse_salary_file, validate_columns


@dataclass
class PayslipResult:
    content: bytes
    content_type: str
    filename: str
    preview_content: bytes
    preview_filename: str


def generate_payslips(
    salary_bytes: bytes, company: CompanyInfo, logo_bytes: bytes | None
) -> PayslipResult:
    data = parse_salary_file(salary_bytes)
    missing = validate_columns(data)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns in Excel: {missing_cols}")

    file_pairs = _build_payslip_files(data, company, logo_bytes)
    if len(file_pairs) == 1:
        filename, pdf_bytes = file_pairs[0]
        return PayslipResult(
            content=pdf_bytes,
            content_type="application/pdf",
            filename=filename,
            preview_content=pdf_bytes,
            preview_filename=filename,
        )

    zip_bytes = build_zip(file_pairs)
    preview_name, preview_bytes = file_pairs[0]
    return PayslipResult(
        content=zip_bytes,
        content_type="application/zip",
        filename="payslips.zip",
        preview_content=preview_bytes,
        preview_filename=preview_name,
    )


def _build_payslip_files(
    data: pd.DataFrame, company: CompanyInfo, logo_bytes: bytes | None
) -> list[tuple[str, bytes]]:
    file_pairs: list[tuple[str, bytes]] = []
    for _, row in data.iterrows():
        employee_name = str(row.get("employee_name", "employee")).strip().replace(" ", "_")
        employee_id = str(row.get("employee_id", "id")).strip().replace(" ", "_")
        pdf_bytes = build_payslip_pdf(row, company, logo_bytes)
        filename = f"payslip_{employee_name}_{employee_id}.pdf"
        file_pairs.append((filename, pdf_bytes))
    return file_pairs

