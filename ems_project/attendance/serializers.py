from rest_framework import serializers
from .models import Attendance, LeaveRequest
from employees.serializers import EmployeeSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = '__all__'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = '__all__'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def get_approved_by_name(self, obj):
        return f"{obj.approved_by.first_name} {obj.approved_by.last_name}" if obj.approved_by else None

    def validate(self, data):
        # Custom validation for leave requests
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be later than end date")
        
        # Calculate total days
        data['total_days'] = (data['end_date'] - data['start_date']).days + 1
        
        return data

    def create(self, validated_data):
        # Custom create method with additional logic
        leave_request = LeaveRequest.objects.create(**validated_data)
        
        # Optional: Send notification or trigger workflow
        # self.send_leave_request_notification(leave_request)
        
        return leave_request
