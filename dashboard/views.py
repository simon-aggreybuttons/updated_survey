from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime
from typing import Any
from xml.sax.saxutils import escape

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View

from survey.models import Question, Region, Sector, Survey
from survey.services import get_dashboard_stats


class DashboardLoginView(View):
    """Custom login view for the dashboard so the flow feels native."""

    template_name = 'dashboard/login.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect('dashboard_home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        form = AuthenticationForm()
        next_url = request.GET.get('next', reverse('dashboard_home'))
        return render(request, self.template_name, {'form': form, 'next': next_url})

    def post(self, request: HttpRequest) -> HttpResponse:
        next_url = request.POST.get('next') or reverse('dashboard_home')
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url)
        return render(request, self.template_name, {'form': form, 'next': next_url})


class DashboardLogoutView(View):
    """Log the user out and redirect back to the public survey home."""

    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('survey_start')


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard with survey statistics and trends."""

    template_name = 'dashboard/dashboard.html'
    login_url = '/dashboard/login/'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        surveys = Survey.objects.all()
        completed = surveys.filter(status='completed')
        stats = get_dashboard_stats()
        context['total_surveys'] = surveys.count()
        context['today_surveys'] = surveys.filter(started_at__date=timezone.now().date()).count()
        context['completed_surveys'] = completed.count()
        context['incomplete_surveys'] = surveys.filter(status__in=['in_progress', 'abandoned']).count()
        context['questions'] = Question.objects.filter(active=True)
        context['sectors'] = Sector.objects.filter(active=True)
        context['regions'] = Region.objects.filter(active=True)
        context['total_responses'] = stats['total_responses']
        context['responses_by_sector'] = stats['responses_by_sector']
        context['gender_distribution'] = stats['gender_distribution']
        context['region_distribution'] = stats['region_distribution']
        context['satisfaction_average'] = stats['satisfaction_average']
        context['satisfaction_distribution'] = stats['satisfaction_distribution']
        context['survey_rows'] = stats['rows']
        return context


class DashboardExportView(LoginRequiredMixin, View):
    """Export completed survey responses as CSV or Excel."""

    login_url = '/dashboard/login/'

    def get(self, request: HttpRequest, format: str) -> HttpResponse:
        stats = get_dashboard_stats()
        rows = stats['rows']
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="gcsi_responses.csv"'
            writer = csv.writer(response)
            writer.writerow(['Survey ID', 'Started At', 'Completed At', 'Sector', 'Gender', 'Region', 'Satisfaction Score'])
            for row in rows:
                writer.writerow([
                    row['survey_id'],
                    row['started_at'].isoformat() if row['started_at'] else '',
                    row['completed_at'].isoformat() if row['completed_at'] else '',
                    row['sector'],
                    row['gender'],
                    row['region'],
                    row['satisfaction_score'],
                ])
            return response

        if format == 'excel':
            output = io.BytesIO()
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as workbook:
                workbook.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>''')
                workbook.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>''')
                workbook.writestr('docProps/app.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>GCSI Survey</Application></Properties>''')
                workbook.writestr('docProps/core.xml', f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>GCSI Survey Responses</dc:title><dc:creator>GitHub Copilot</dc:creator><cp:revision>1</cp:revision><dcterms:created xsi:type="dcterms:W3CDTF">{datetime.utcnow().replace(microsecond=0).isoformat()}Z</dcterms:created></cp:coreProperties>''')
                workbook.writestr('xl/workbook.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Responses" sheetId="1" r:id="rId1"/></sheets></workbook>''')
                workbook.writestr('xl/_rels/workbook.xml.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''')
                workbook.writestr('xl/styles.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="1"><fill><patternFill patternType="none"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>''')

                sheet_rows = [['Survey ID', 'Started At', 'Completed At', 'Sector', 'Gender', 'Region', 'Satisfaction Score']]
                for row in rows:
                    sheet_rows.append([
                        row['survey_id'],
                        row['started_at'].isoformat() if row['started_at'] else '',
                        row['completed_at'].isoformat() if row['completed_at'] else '',
                        row['sector'],
                        row['gender'],
                        row['region'],
                        row['satisfaction_score'],
                    ])

                sheet_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
                for index, row in enumerate(sheet_rows, start=1):
                    sheet_xml.append(f'<row r="{index}">')
                    for col_index, value in enumerate(row, start=1):
                        cell_ref = f'{chr(64 + col_index)}{index}'
                        if isinstance(value, (int, float)):
                            sheet_xml.append(f'<c r="{cell_ref}"><v>{value}</v></c>')
                        else:
                            sheet_xml.append(f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
                    sheet_xml.append('</row>')
                sheet_xml.append('</sheetData></worksheet>')
                workbook.writestr('xl/worksheets/sheet1.xml', ''.join(sheet_xml))

            output.seek(0)
            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="gcsi_responses.xlsx"'
            return response

        return HttpResponse('Unsupported format', status=400)


class PasswordChangeView(LoginRequiredMixin, View):
    """Allow logged-in admin users to change their password."""

    template_name = 'dashboard/password_change.html'
    login_url = '/dashboard/login/'

    def get(self, request: HttpRequest) -> HttpResponse:
        form = PasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('password_change_done')
        return render(request, self.template_name, {'form': form})


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    """Show success message after password change."""

    template_name = 'dashboard/password_change_done.html'
    login_url = '/dashboard/login/'
