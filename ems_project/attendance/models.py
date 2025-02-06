from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee

# Create your models here.

class Attendance(models.Model):
    ATTENDANCE_STATUS = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('WFH', 'Work From Home')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=3, choices=ATTENDANCE_STATUS, default='A')
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # Optional notes or reason for absence/late
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('CL', 'Casual Leave'),
        ('SL', 'Sick Leave'),
        ('PL', 'Privilege Leave'),
        ('ML', 'Maternity Leave'),
        ('PT', 'Paternity Leave')
    ]

    LEAVE_STATUS = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=2, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    reason = models.TextField()
    status = models.CharField(max_length=1, choices=LEAVE_STATUS, default='P')
    
    # Optional approver details
    approved_by = models.ForeignKey(Employee, 
                                    on_delete=models.SET_NULL, 
                                    null=True, 
                                    related_name='approved_leaves',
                                    blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"
