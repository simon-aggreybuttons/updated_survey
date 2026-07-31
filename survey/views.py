from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from .forms import SurveyAnswerForm
from .models import Question, Region, Sector, Survey
from .services import (
    format_answer_display,
    get_active_questions,
    get_question_by_number,
    get_session_answers,
    save_session_answers,
    save_survey_responses,
)
from .utils import (
    get_client_ip,
    get_sector_company_label,
    get_sector_companies,
    get_user_agent,
    render_question_text,
)


class SurveyStartView(TemplateView):
    """Landing page for the survey."""

    template_name = 'survey/start.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['questions'] = get_active_questions()
        context['sectors'] = Sector.objects.filter(active=True)
        context['regions'] = Region.objects.filter(active=True)
        return context

    def post(self, request: HttpRequest) -> HttpResponse:
        survey = Survey.objects.create(
            session_key=request.session.session_key or 'guest',
            browser=get_user_agent(request),
            device=request.headers.get('User-Agent', '')[:100],
            ip_address=get_client_ip(request),
        )
        request.session['survey_id'] = survey.id
        request.session['current_question'] = 1
        save_session_answers(request, {})
        return redirect('survey_question', number=1)


class SurveyQuestionView(View):
    """Render a single question and persist answers in the session."""

    template_name = 'survey/question.html'

    def get_dynamic_choices(self, question: Question, selected_sector: str | None) -> list[dict[str, str]] | None:
        if question.number == 3:
            companies = get_sector_companies(selected_sector)
            if companies:
                return [{'text': name, 'value': name} for name in companies]
        return None

    def get(self, request: HttpRequest, number: int) -> HttpResponse:
        survey_id = request.session.get('survey_id')
        if not survey_id:
            return redirect('survey_start')

        survey = Survey.objects.get(pk=survey_id)
        question = get_question_by_number(number)
        if not question:
            return redirect('survey_review')

        questions = get_active_questions()
        total_questions = len(questions)
        current_index = next((index for index, item in enumerate(questions) if item.number == number), 0)
        progress = int((current_index + 1) / total_questions * 100) if total_questions else 0
        previous_question_number = questions[current_index - 1].number if current_index > 0 else None
        answers = get_session_answers(request)
        initial = answers.get(str(question.id))
        matrix_initial = initial if isinstance(initial, dict) else {}
        matrix_rows = [
            {
                'row': row,
                'selected': matrix_initial.get(row.label, ''),
            }
            for row in question.matrix_rows_data
        ]

        selected_sector = request.session.get('selected_sector')
        selected_company = request.session.get('selected_company')
        question_title = render_question_text(question.title, selected_sector, selected_company)
        question_description = render_question_text(question.description, selected_sector, selected_company)
        choices = self.get_dynamic_choices(question, selected_sector)

        return render(request, self.template_name, {
            'survey': survey,
            'question': question,
            'questions': questions,
            'total_questions': total_questions,
            'question_number': current_index + 1,
            'progress': progress,
            'answers': answers,
            'initial_value': initial,
            'matrix_initial': matrix_initial,
            'matrix_rows': matrix_rows,
            'previous_question_number': previous_question_number,
            'question_title': question_title,
            'question_description': question_description,
            'choices': choices,
        })

    def post(self, request: HttpRequest, number: int) -> HttpResponse:
        survey_id = request.session.get('survey_id')
        if not survey_id:
            return redirect('survey_start')

        survey = Survey.objects.get(pk=survey_id)
        question = get_question_by_number(number)
        if not question:
            return redirect('survey_review')

        questions = get_active_questions()
        form = SurveyAnswerForm(request.POST)
        answers = get_session_answers(request)

        if question.question_type == 'matrix':
            payload: dict[str, Any] = {}
            validation_errors = []
            selected_values: list[str] = []
            missing_rows = []

            for row in question.matrix_rows_data:
                row_name = f'matrix_{row.id}'
                value = request.POST.get(row_name, '').strip()
                post_data = request.POST.getlist(row_name)

                if len(post_data) > 1:
                    validation_errors.append('Please select one option per row.')

                if not value:
                    missing_rows.append(row.label)
                else:
                    payload[row.label] = value
                    selected_values.append(value)

            if missing_rows:
                validation_errors.append('Please answer all columns in the matrix before proceeding.')

            if question.number in (5, 6) and len(set(selected_values)) != len(selected_values):
                validation_errors.append('Please choose a unique rating value for each row.')

            if validation_errors:
                messages.error(request, 'Please answer all columns in the matrix and use unique ratings.')
                return redirect('survey_question', number=number)

            answers[str(question.id)] = payload
        elif question.question_type == 'checkbox':
            selected = request.POST.getlist('answer')
            if question.required and not selected:
                messages.error(request, 'Please select at least one option.')
                return redirect('survey_question', number=number)
            answers[str(question.id)] = selected
        elif question.question_type == 'dropdown':
            selected = request.POST.get('answer', '').strip()
            if question.required and not selected:
                messages.error(request, 'Please choose an option.')
                return redirect('survey_question', number=number)
            answers[str(question.id)] = selected
        else:
            value = request.POST.get('answer', '')
            if question.required and not str(value).strip():
                messages.error(request, 'This question is required.')
                return redirect('survey_question', number=number)
            answers[str(question.id)] = value

        if question.number == 1:
            selected_sector = answers.get(str(question.id))
            if selected_sector:
                request.session['selected_sector'] = selected_sector

        save_session_answers(request, answers)
        current_index = next((index for index, item in enumerate(questions) if item.number == number), 0)
        next_question = questions[current_index + 1] if current_index + 1 < len(questions) else None
        if next_question:
            request.session['current_question'] = next_question.number
            return redirect('survey_question', number=next_question.number)

        request.session['current_question'] = None
        return redirect('survey_review')


class SurveyReviewView(TemplateView):
    """Review all captured answers before final submission."""

    template_name = 'survey/summary.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        survey_id = self.request.session.get('survey_id')
        if not survey_id:
            context['survey'] = None
            return context
        survey = Survey.objects.get(pk=survey_id)
        answers = get_session_answers(self.request)
        questions = list(Question.objects.filter(active=True).order_by('order', 'number'))
        context['survey'] = survey
        context['questions'] = questions
        context['answers'] = answers
        context['review_items'] = [
            {
                'question': question,
                'answer': answers.get(str(question.id), ''),
                'display_answer': format_answer_display(answers.get(str(question.id), '')),
            }
            for question in questions
            if answers.get(str(question.id), '')
        ]
        return context


class SurveyClearView(View):
    """Clear the current survey session and return the user to the start."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        session_key = request.session.session_key
        if session_key:
            request.session.pop(f'survey_answers:{session_key}', None)
        for key in ['survey_id', 'current_question', 'selected_sector', 'selected_company', 'completed']:
            request.session.pop(key, None)
        return redirect('survey_start')


class SurveySubmitView(View):
    """Persist session answers to the database and mark the survey complete."""

    def post(self, request: HttpRequest) -> HttpResponse:
        survey_id = request.session.get('survey_id')
        if not survey_id:
            return redirect('survey_start')

        survey = Survey.objects.get(pk=survey_id)
        if survey.status == 'completed':
            return redirect('survey_complete')

        answers = get_session_answers(request)
        save_survey_responses(survey, answers)
        survey.status = 'completed'
        survey.completed_at = timezone.now()
        survey.browser = get_user_agent(request)
        survey.device = request.headers.get('User-Agent', '')[:100]
        survey.ip_address = get_client_ip(request)
        survey.save(update_fields=['status', 'completed_at', 'browser', 'device', 'ip_address'])
        request.session['completed'] = True
        return redirect('survey_complete')


class SurveyCompleteView(TemplateView):
    """Thank-you page shown after submission."""

    template_name = 'survey/complete.html'


class SurveyErrorView(TemplateView):
    """Error page for invalid flows."""

    template_name = 'survey/error.html'
