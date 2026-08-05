from django.test import TestCase
from django.core.management import call_command

from .models import Choice, Question, Survey
from .services import format_answer_display, save_survey_responses
from .utils import get_sector_companies, render_question_text


class SurveyResponseStorageTests(TestCase):
    def test_save_survey_responses_updates_existing_answers_without_duplicates(self):
        survey = Survey.objects.create(status='in_progress')
        question = Question.objects.create(number=1, title='Sector', question_type='radio', required=True)

        answers = {str(question.id): 'Telecommunications'}
        save_survey_responses(survey, answers)
        save_survey_responses(survey, answers)

        self.assertEqual(survey.responses.count(), 1)
        self.assertEqual(survey.responses.get(question=question).answer, 'Telecommunications')

    def test_format_answer_display_converts_lists_and_dicts_to_readable_text(self):
        self.assertEqual(format_answer_display(['Zenith Bank (Ghana) Limited']), 'Zenith Bank (Ghana) Limited')
        self.assertEqual(format_answer_display({'Trust': '10', 'Look and feel': '9'}), 'Trust: 10; Look and feel: 9')

    def test_shows_scale_guidance_for_numeric_rating_radio_questions(self):
        question = Question.objects.create(number=2, title='Satisfaction', question_type='radio', required=True)
        Choice.objects.create(question=question, text='1', value='1', order=1)
        Choice.objects.create(question=question, text='2', value='2', order=2)
        Choice.objects.create(question=question, text='3', value='3', order=3)

        self.assertTrue(question.shows_scale_guidance())

    def test_render_question_text_replaces_bank_specific_terms_with_sector_labels(self):
        text = 'Please select ALL_THE_BANKS in the SELECTED_SECTOR sector. If the BANK is not listed, please type it in the space provided for Others.'

        rendered = render_question_text(text, 'Hospitality', 'The African Regent Hotel')

        self.assertIn('hotels', rendered)
        self.assertIn('Hospitality', rendered)
        self.assertIn('hotel', rendered)
        self.assertNotIn('BANK', rendered)

    def test_get_sector_companies_uses_glico_life_label_for_insurance(self):
        self.assertIn('Glico Life', get_sector_companies('Insurance'))
        self.assertNotIn('Glico', get_sector_companies('Insurance'))

    def test_render_question_text_replaces_legacy_singular_placeholder_by_sector(self):
        text = 'If the banks_SINGULAR is not listed, please type it in the space provided for Others.'

        self.assertEqual(
            render_question_text(text, 'Banking'),
            'If the Bank is not listed, please type it in the space provided for Others.',
        )
        self.assertEqual(
            render_question_text(text, 'Hospitality'),
            'If the Hotel is not listed, please type it in the space provided for Others.',
        )
        self.assertEqual(
            render_question_text(
                'If the utility companies_SINGULAR is not listed, please type it in the space provided for Others.',
                'Utilities',
            ),
            'If the Utility company is not listed, please type it in the space provided for Others.',
        )

    def test_seed_deactivates_legacy_duplicate_page_four(self):
        Question.objects.create(number=4, title='Duplicate company question', question_type='checkbox')

        call_command('seed_survey')

        self.assertTrue(Question.objects.get(number=4).active)
        self.assertTrue(Question.objects.get(number=3).active)
        self.assertTrue(Question.objects.get(number=5).active)

    def test_seed_creates_ranking_question_after_page_four(self):
        call_command('seed_survey')

        question = Question.objects.get(number=4)
        self.assertEqual(question.question_type, 'matrix')
        self.assertTrue(question.active)
        self.assertIn('Trust', [row.label for row in question.questionmatrixrow_set.all()])
        self.assertEqual(question.questionmatrixrow_set.count(), 10)

    def test_clear_survey_returns_to_start_and_clears_session(self):
        session = self.client.session
        session['survey_id'] = 123
        session['current_question'] = 5
        session['selected_sector'] = 'Utilities'
        session['selected_company'] = 'Ghana Water Company'
        session['completed'] = True
        session.save()

        response = self.client.get('/survey/clear/')

        self.assertRedirects(response, '/survey/start/')
        self.assertNotIn('survey_id', self.client.session)
        self.assertNotIn('current_question', self.client.session)
        self.assertNotIn('selected_sector', self.client.session)
        self.assertNotIn('selected_company', self.client.session)
        self.assertNotIn('completed', self.client.session)

    def test_blank_required_text_answer_is_rejected(self):
        question = Question.objects.create(number=16, title='What is your age? Please give your exact age in figures.', question_type='text', required=True)
        survey = Survey.objects.create(status='in_progress')

        session = self.client.session
        session['survey_id'] = survey.id
        session['current_question'] = question.number
        session.save()

        response = self.client.post(f'/survey/question/{question.number}/', {'answer': ''})

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/survey/question/{question.number}/', response['Location'])

    def test_required_text_question_with_none_initial_value_still_validates(self):
        question = Question.objects.create(number=25, title='What is your impression?', question_type='text', required=True)
        survey = Survey.objects.create(status='in_progress')

        session = self.client.session
        session['survey_id'] = survey.id
        session['current_question'] = question.number
        session.save()

        response = self.client.post(f'/survey/question/{question.number}/', {'answer': 'None'})

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/survey/question/{question.number}/', response['Location'])
