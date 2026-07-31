from django.urls import path

from .views_api import (
    QuestionDetailAPIView,
    QuestionListAPIView,
    SaveResponseAPIView,
    StatisticsAPIView,
    SubmitSurveyAPIView,
)

urlpatterns = [
    path('questions/', QuestionListAPIView.as_view(), name='api_questions'),
    path('question/<int:pk>/', QuestionDetailAPIView.as_view(), name='api_question_detail'),
    path('save/', SaveResponseAPIView.as_view(), name='api_save'),
    path('submit/', SubmitSurveyAPIView.as_view(), name='api_submit'),
    path('statistics/', StatisticsAPIView.as_view(), name='api_statistics'),
]
