from django.db import models
from django.core.validators import MinValueValidator
from employees.models import Employee
from attendance.models import LeaveRequest

# Create your models here.

class SalaryComponent(models.Model):
    COMPONENT_TYPES = [
        ('BASIC', 'Basic Salary'),
        ('HRA', 'House Rent Allowance'),
        ('DA', 'Dearness Allowance'),
        ('BONUS', 'Performance Bonus'),
        ('OTHER', 'Other Allowance')
    ]

    name = models.CharField(max_length=50, unique=True)
    component_type = models.CharField(max_length=10, choices=COMPONENT_TYPES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, 
                                     validators=[MinValueValidator(0)],
                                     help_text="Percentage of base salary")
    is_taxable = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PayrollPeriod(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.start_date} to {self.end_date}"

class Payslip(models.Model):
    PAYMENT_MODES = [
        ('BANK', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    
    # Earnings
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    pf_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2)
    leave_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totals
    gross_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Details
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES, default='BANK')
    payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Status
    is_paid = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('employee', 'payroll_period')
        ordering = ['-payroll_period__start_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period}"

    def calculate_leave_deductions(self):
        """
        Calculate salary deductions based on unpaid leaves
        """
        unpaid_leaves = LeaveRequest.objects.filter(
            employee=self.employee,
            start_date__gte=self.payroll_period.start_date,
            end_date__lte=self.payroll_period.end_date,
            status='A'  # Only approved leaves
        )
        
        total_unpaid_days = sum(leave.total_days for leave in unpaid_leaves)
        daily_salary = self.basic_salary / 30  # Assuming 30 days in a month
        
        return total_unpaid_days * daily_salary
