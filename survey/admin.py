from django.contrib import admin

from .models import Choice, Question, QuestionMatrixRow, Region, Sector, Survey, SurveyResponse


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'order')
    list_filter = ('active',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'order')
    list_filter = ('active',)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionMatrixRowInline(admin.TabularInline):
    model = QuestionMatrixRow
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'question_type', 'active', 'required')
    list_filter = ('active', 'question_type')
    search_fields = ('title', 'description')
    inlines = [ChoiceInline, QuestionMatrixRowInline]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'started_at', 'completed_at', 'session_key')
    list_filter = ('status', 'started_at')
    search_fields = ('session_key',)


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'question', 'created_at')
    list_filter = ('created_at',)
