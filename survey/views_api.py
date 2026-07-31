from __future__ import annotations

from typing import Any

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

from .models import Question, Survey, SurveyResponse
from .services import get_session_answers, save_session_answers
from .serializers import QuestionSerializer, SurveySerializer
from .utils import get_client_ip, get_user_agent


class QuestionListAPIView(APIView):
    """Return a list of active questions."""

    def get(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        questions = Question.objects.filter(active=True).order_by('number')
        serializer = QuestionSerializer(questions, many=True)
        return JsonResponse(serializer.data, safe=False)


class QuestionDetailAPIView(APIView):
    """Return a single question."""

    def get(self, request, pk: int, *args: Any, **kwargs: Any) -> JsonResponse:
        question = Question.objects.filter(active=True, pk=pk).first()
        if not question:
            return JsonResponse({'detail': 'Not found'}, status=404)
        serializer = QuestionSerializer(question)
        return JsonResponse(serializer.data)


class SaveResponseAPIView(APIView):
    """Save a response payload to the current session."""

    def post(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        answers = get_session_answers(request)
        data = request.data or {}
        answers.update(data)
        save_session_answers(request, answers)
        return JsonResponse({'status': 'saved'})


class SubmitSurveyAPIView(APIView):
    """Submit the current survey response payload."""

    def post(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        survey = Survey.objects.create(
            session_key=request.session.session_key or 'guest',
            browser=get_user_agent(request),
            device=request.headers.get('User-Agent', '')[:100],
            ip_address=get_client_ip(request),
        )
        answers = request.data or {}
        for question_id, value in answers.items():
            question = Question.objects.filter(pk=int(question_id)).first()
            if question:
                SurveyResponse.objects.create(survey=survey, question=question, answer=value)
        survey.status = 'completed'
        survey.save(update_fields=['status'])
        return JsonResponse({'status': 'submitted', 'survey_id': survey.id})


class StatisticsAPIView(APIView):
    """Expose simple survey statistics."""

    def get(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        return JsonResponse({
            'total_surveys': Survey.objects.count(),
            'completed_surveys': Survey.objects.filter(status='completed').count(),
        })
