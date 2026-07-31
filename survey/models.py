from __future__ import annotations

from django.db import models
from django.utils import timezone


class Sector(models.Model):
    """A sector that can be selected in the survey."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'name')

    def __str__(self) -> str:
        return self.name


class Region(models.Model):
    """A geographic region for the demographics section."""

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'name')

    def __str__(self) -> str:
        return self.name


class Question(models.Model):
    """A survey question rendered dynamically from the database."""

    QUESTION_TYPES = [
        ('radio', 'Radio Button'),
        ('checkbox', 'Checkbox'),
        ('dropdown', 'Dropdown'),
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('matrix', 'Matrix Question'),
    ]

    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    matrix_rows = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ('order', 'number')

    def __str__(self) -> str:
        return f"Q{self.number}: {self.title}"

    @property
    def choices(self):
        return self.choice_set.filter(active=True).order_by('order', 'id')

    @property
    def matrix_rows_data(self):
        return self.questionmatrixrow_set.filter(active=True).order_by('order', 'id')

    def shows_scale_guidance(self):
        """Return True for questions that use a 1-up numeric rating scale."""
        supported_types = {'radio', 'dropdown', 'matrix'}
        if self.question_type not in supported_types:
            return False

        values = []
        for choice in self.choices:
            raw_value = choice.value or choice.text
            try:
                values.append(int(raw_value))
            except (TypeError, ValueError):
                continue

        if len(values) < 2:
            return False

        sorted_values = sorted(values)
        expected_values = list(range(1, max(sorted_values) + 1))
        return sorted_values == expected_values and min(sorted_values) == 1


class Choice(models.Model):
    """Answer choice for a question."""

    question = models.ForeignKey(Question, related_name='choice_set', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('order', 'id')

    def __str__(self) -> str:
        return self.text


class QuestionMatrixRow(models.Model):
    """Row definition for matrix style questions."""

    question = models.ForeignKey(Question, related_name='questionmatrixrow_set', on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('order', 'id')

    def __str__(self) -> str:
        return self.label


class Survey(models.Model):
    """A single survey submission attempt."""

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    browser = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    year = models.PositiveIntegerField(default=timezone.now().year)

    class Meta:
        ordering = ('-started_at',)

    def __str__(self) -> str:
        return f"Survey #{self.id}"


class SurveyResponse(models.Model):
    """An individual answer captured during survey completion."""

    survey = models.ForeignKey(Survey, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='responses', on_delete=models.CASCADE)
    matrix_row = models.ForeignKey(QuestionMatrixRow, blank=True, null=True, on_delete=models.SET_NULL)
    answer = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('question__number', 'created_at')

    def __str__(self) -> str:
        return f"{self.survey_id} / Q{self.question.number}"
