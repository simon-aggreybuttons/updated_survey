from __future__ import annotations

from django import forms


class SurveyAnswerForm(forms.Form):
    """Generic validation form for survey answers."""

    answer = forms.CharField(required=False)

    def clean_answer(self):
        data = self.cleaned_data.get('answer')
        if data is None:
            return ''
        return data
