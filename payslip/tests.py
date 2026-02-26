from django.test import TestCase
from django.urls import reverse


class ProposalQuotationViewTests(TestCase):
    def test_get_proposal_quotation_page(self):
        response = self.client.get(reverse('proposal_quotation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proposal Quotation Generator')

    def test_post_generates_complete_proposal_text(self):
        response = self.client.post(
            reverse('proposal_quotation'),
            {
                'client_name': 'ABC College of Arts and Science',
                'client_location': 'Coimbatore, Tamil Nadu',
                'institution_type': 'AUTONOMOUS',
                'proposal_date': '2026-02-13',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ABC College of Arts and Science')
        self.assertContains(response, 'Coimbatore, Tamil Nadu')
        self.assertContains(response, 'AUTONOMOUS')

        required_sections = [
            '1. SUBJECT & INTRODUCTION',
            '2. PROJECT OVERVIEW',
            '3. ABOUT AVEON INFOTECH',
            '4. SCOPE OF WORK / PROJECT DETAILS',
            '5. IMPLEMENTATION METHODOLOGY (PHASE-WISE)',
            '6. PROJECT TIMELINE WITH MILESTONES',
            '7. PROJECT INVESTMENT',
            '8. SUPPORT & MAINTENANCE MODEL',
            '9. DETAILED TERMS & CONDITIONS',
            '10. WHY PARTNER WITH AVEON INFOTECH',
            '11. AUTHORIZATION & SIGNATURE',
        ]

        proposal_text = response.context['proposal_text']
        for section in required_sections:
            self.assertIn(section, proposal_text)

        self.assertIn('GST @18%', proposal_text)
        self.assertIn('Courts at Coimbatore, Tamil Nadu shall have exclusive jurisdiction.', proposal_text)


    def test_post_download_returns_text_file(self):
        response = self.client.post(
            reverse('proposal_quotation'),
            {
                'client_name': 'ABC College of Arts and Science',
                'client_location': 'Coimbatore, Tamil Nadu',
                'institution_type': 'AUTONOMOUS',
                'proposal_date': '2026-02-13',
                'action': 'download',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertIn('attachment; filename="aveon_cms_erp_proposal.txt"', response['Content-Disposition'])
        text = response.content.decode('utf-8')
        self.assertIn('1. SUBJECT & INTRODUCTION', text)
        self.assertIn('11. AUTHORIZATION & SIGNATURE', text)


    def test_school_institution_type_is_available(self):
        response = self.client.get(reverse('proposal_quotation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SCHOOL')

    def test_post_download_returns_pdf_file(self):
        response = self.client.post(
            reverse('proposal_quotation'),
            {
                'client_name': 'ABC School',
                'client_location': 'Coimbatore, Tamil Nadu',
                'institution_type': 'SCHOOL',
                'proposal_date': '2026-02-13',
                'action': 'download_pdf',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="aveon_cms_erp_proposal.pdf"', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF-'))
