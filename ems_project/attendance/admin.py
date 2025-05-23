from django.contrib import admin
from .models import Attendance, LeaveRequest

# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('date', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('-date',)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('-start_date',)
