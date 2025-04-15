from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Department, Employee, Attendance, Performance, LeaveRecord


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'budget', 'established_date', 'active')
    search_fields = ('name', 'location')
    list_filter = ('active',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'position', 'join_date', 'salary', 'is_manager')
    search_fields = ('name', 'email', 'position')
    list_filter = ('department', 'is_manager', 'gender')
    list_select_related = ('department',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__name',)
    autocomplete_fields = ['employee']


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'score', 'review_date', 'next_review_date', 'reviewer')
    list_filter = ('score', 'review_date')
    search_fields = ('employee__name', 'reviewer__name')


@admin.register(LeaveRecord)
class LeaveRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'days', 'status', 'approved_by')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('employee__name', 'approved_by__name')
    autocomplete_fields = ['employee', 'approved_by']
