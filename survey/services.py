from __future__ import annotations

import json
from collections import Counter
from statistics import mean
from typing import Any

from django.http import HttpRequest

from .models import Question, Survey, SurveyResponse


def get_active_questions() -> list[Question]:
    return list(Question.objects.filter(active=True).order_by('order', 'number'))


def get_question_by_number(number: int) -> Question | None:
    return Question.objects.filter(active=True, number=number).select_related().first()


def get_session_answers(request: HttpRequest) -> dict[str, Any]:
    session_key = f"survey_answers:{request.session.session_key}"
    data = request.session.get(session_key, {})
    if isinstance(data, str):
        return json.loads(data)
    return data


def save_session_answers(request: HttpRequest, answers: dict[str, Any]) -> None:
    session_key = f"survey_answers:{request.session.session_key}"
    request.session[session_key] = answers
    request.session.modified = True


def normalize_answer_value(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return '; '.join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return value


def format_answer_display(value: Any) -> str:
    if value in (None, ''):
        return ''
    if isinstance(value, (list, tuple)):
        formatted_items = [format_answer_display(item) for item in value]
        return ', '.join(item for item in formatted_items if item)
    if isinstance(value, dict):
        formatted_items = [f'{key}: {format_answer_display(val)}' for key, val in value.items() if format_answer_display(val)]
        return '; '.join(formatted_items)
    return str(value)


def parse_numeric_score(value: Any) -> float | None:
    if value in (None, ''):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = ''.join(char for char in value if char.isdigit() or char in '.-')
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                return None
    return None


def save_survey_responses(survey: Survey, answers: dict[str, Any]) -> None:
    for question_id, value in answers.items():
        question = Question.objects.get(pk=int(question_id))
        existing = survey.responses.filter(question=question).first()
        if existing:
            existing.answer = value
            existing.save(update_fields=['answer'])
        else:
            SurveyResponse.objects.create(survey=survey, question=question, answer=value)


def get_completed_survey_rows() -> list[dict[str, Any]]:
    completed_surveys = Survey.objects.filter(status='completed').prefetch_related('responses__question').order_by('-completed_at')
    rows: list[dict[str, Any]] = []
    for survey in completed_surveys:
        answers_by_number: dict[int, Any] = {}
        for response in survey.responses.all():
            answers_by_number[response.question.number] = normalize_answer_value(response.answer)
        rows.append({
            'survey_id': survey.id,
            'started_at': survey.started_at,
            'completed_at': survey.completed_at,
            'sector': answers_by_number.get(1, ''),
            'gender': answers_by_number.get(15, ''),
            'region': answers_by_number.get(18, ''),
            'satisfaction_score': parse_numeric_score(answers_by_number.get(2)) or parse_numeric_score(answers_by_number.get(9)),
            'answers': answers_by_number,
        })
    return rows


def get_dashboard_stats() -> dict[str, Any]:
    rows = get_completed_survey_rows()
    sector_counts = Counter(row['sector'] for row in rows if row['sector'])
    gender_counts = Counter(row['gender'] for row in rows if row['gender'])
    region_counts = Counter(row['region'] for row in rows if row['region'])
    satisfaction_scores = [row['satisfaction_score'] for row in rows if row['satisfaction_score'] is not None]

    return {
        'total_responses': len(rows),
        'responses_by_sector': [
            {'label': label, 'value': value}
            for label, value in sorted(sector_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        'gender_distribution': [
            {'label': label, 'value': value}
            for label, value in sorted(gender_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        'region_distribution': [
            {'label': label, 'value': value}
            for label, value in sorted(region_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        'satisfaction_average': round(mean(satisfaction_scores), 2) if satisfaction_scores else 0,
        'satisfaction_distribution': [
            {'label': label, 'value': value}
            for label, value in sorted(Counter(str(int(score)) for score in satisfaction_scores).items(), key=lambda item: item[0])
        ],
        'rows': rows,
    }
