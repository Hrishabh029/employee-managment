from django.contrib import admin
from .models import Employee, Department, EmployeeDocument, Performance

# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'department', 'employment_type')
    list_filter = ('department', 'employment_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name', 'last_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'uploaded_at')
    list_filter = ('document_type',)
    search_fields = ('employee__first_name', 'employee__last_name')

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'review_date', 'overall_score')
    list_filter = ('review_date',)
    search_fields = ('employee__first_name', 'employee__last_name')
