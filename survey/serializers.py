from __future__ import annotations

from rest_framework import serializers

from .models import Choice, Question, Survey, SurveyResponse


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text', 'value', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'number', 'title', 'description', 'question_type', 'required', 'choices')


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = ('question', 'answer')


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'status', 'started_at', 'completed_at')
