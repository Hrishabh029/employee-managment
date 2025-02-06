from django.contrib import admin
from .models import SalaryComponent, PayrollPeriod, Payslip

# Register your models here.

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'component_type', 'percentage', 'is_taxable')
    list_filter = ('component_type', 'is_taxable')
    search_fields = ('name',)

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'is_processed', 'processed_at')
    list_filter = ('is_processed', 'start_date')
    ordering = ('-start_date',)

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll_period', 'basic_salary', 'net_salary', 'is_paid')
    list_filter = ('is_paid', 'payroll_period')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('-payroll_period__start_date',)
