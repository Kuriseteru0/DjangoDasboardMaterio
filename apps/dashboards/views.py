from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.views.generic import TemplateView
from .models import College, Organization, OrgMember, Program, Student
from web_project import TemplateLayout
import json
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['colleges_count'] = College.objects.count()
        context['organizations_count'] = Organization.objects.count()
        context['programs_count'] = Program.objects.count()
        context['students_count'] = Student.objects.count()
        
        # Total Enrolled This Year
        now = timezone.now()
        context['students_this_year'] = Student.objects.filter(created_at__year=now.year).count()

        # New Students This Week
        week_start = now - timezone.timedelta(days=now.weekday())
        context['new_students_week'] = Student.objects.filter(created_at__gte=week_start).count()

        # Example: Total Earnings (replace with your logic if needed)
        context['total_earnings'] = 0  # Placeholder, update with your calculation

        # Example: Total Profit (replace with your logic if needed)
        context['total_profit'] = 0  # Placeholder, update with your calculation

        # Weekly Overview Chart Data (students enrolled per week)
        students_weekly = (
            Student.objects
            .annotate(week=TruncDate('created_at'))
            .values('week')
            .annotate(count=Count('id'))
            .order_by('week')
        )
        context['weekly_chart_labels'] = json.dumps([str(item['week']) for item in students_weekly])
        context['weekly_chart_data'] = json.dumps([item['count'] for item in students_weekly])

        students = Student.objects.select_related('program').all()[:63]
        for idx, student in enumerate(students[:10]):
            context[f'student{idx}'] = {
                'firstname': student.firstname,
                'lastname': student.lastname,
                'middlename': student.middlename,
                'student_id': student.student_id,
                'created_at': student.created_at,
                'program': student.program.prog_name if student.program else ''
            }
        
        # Student chart data by date
        students_counts = (
            Student.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        # Ensure at least one data point for chart stability
        if not students_counts:
            context['student_chart_labels'] = json.dumps(["No Data"])
            context['student_chart_data'] = json.dumps([0])
        else:
            context['student_chart_labels'] = json.dumps([str(item['date']) for item in students_counts])
            context['student_chart_data'] = json.dumps([item['count'] for item in students_counts])

        # Organization chart data by date
        org_counts = (
            Organization.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        if not org_counts:
            context['org_chart_labels'] = json.dumps(["No Data"])
            context['org_chart_data'] = json.dumps([0])
        else:
            context['org_chart_labels'] = json.dumps([str(item['date']) for item in org_counts])
            context['org_chart_data'] = json.dumps([item['count'] for item in org_counts])

        # Programs in College of Sciences Donut Chart Data
        # You can filter by college if you have a relation, here we just use all programs as an example
        programs_in_cs = [
            {'label': 'ACS', 'percentage': 25.8},
            {'label': 'MARBIO', 'percentage': 6.2},
            {'label': 'BSIT', 'percentage': 12.4},
            {'label': 'ESSA', 'percentage': 11.9},
            {'label': 'MEDBIO', 'percentage': 16.2},
        ]
        context['programs_in_cs_labels'] = json.dumps([p['label'] for p in programs_in_cs])
        context['programs_in_cs_data'] = json.dumps([p['percentage'] for p in programs_in_cs])

        return context
