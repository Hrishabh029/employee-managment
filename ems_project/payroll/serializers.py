from rest_framework import serializers
from .models import SalaryComponent, PayrollPeriod, Payslip
from employees.serializers import EmployeeSerializer

class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = '__all__'

class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    payroll_period_details = PayrollPeriodSerializer(source='payroll_period', read_only=True)

    class Meta:
        model = Payslip
        fields = '__all__'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def validate(self, data):
        # Validate salary calculations
        if data.get('gross_earnings', 0) < data.get('total_deductions', 0):
            raise serializers.ValidationError("Total deductions cannot exceed gross earnings")
        
        # Ensure net salary is calculated correctly
        data['net_salary'] = data.get('gross_earnings', 0) - data.get('total_deductions', 0)
        
        return data

    def create(self, validated_data):
        # Custom payslip generation logic
        payslip = Payslip.objects.create(**validated_data)
        
        # Optional: Trigger additional payroll processes
        # self.process_payroll_notifications(payslip)
        
        return payslip
