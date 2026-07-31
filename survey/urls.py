from django.urls import include, path

from .views import (
    SurveyCompleteView,
    SurveyErrorView,
    SurveyQuestionView,
    SurveyReviewView,
    SurveyStartView,
    SurveySubmitView,
)

urlpatterns = [
    path('', SurveyStartView.as_view(), name='survey_home'),
    path('api/', include('survey.api_urls')),
    path('start/', SurveyStartView.as_view(), name='survey_start'),
    path('question/<int:number>/', SurveyQuestionView.as_view(), name='survey_question'),
    path('review/', SurveyReviewView.as_view(), name='survey_review'),
    path('submit/', SurveySubmitView.as_view(), name='survey_submit'),
    path('complete/', SurveyCompleteView.as_view(), name='survey_complete'),
    path('error/', SurveyErrorView.as_view(), name='survey_error'),
]
