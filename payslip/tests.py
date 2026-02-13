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
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ABC College of Arts and Science')
        self.assertContains(response, 'Coimbatore, Tamil Nadu')
        self.assertContains(response, 'AUTONOMOUS')

        required_sections = [
            '1. COVER PAGE',
            '2. SUBJECT & INTRODUCTION',
            '3. PROJECT OVERVIEW',
            '4. ABOUT AVEON INFOTECH',
            '5. SCOPE OF WORK / PROJECT DETAILS',
            '6. IMPLEMENTATION METHODOLOGY (PHASE-WISE)',
            '7. PROJECT TIMELINE WITH MILESTONES',
            '8. PROJECT INVESTMENT',
            '9. SUPPORT & MAINTENANCE MODEL',
            '10. DETAILED TERMS & CONDITIONS',
            '11. WHY PARTNER WITH AVEON INFOTECH',
            '12. AUTHORIZATION & SIGNATURE',
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
                'action': 'download',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertIn('attachment; filename="aveon_cms_erp_proposal.txt"', response['Content-Disposition'])
        text = response.content.decode('utf-8')
        self.assertIn('1. COVER PAGE', text)
        self.assertIn('12. AUTHORIZATION & SIGNATURE', text)
