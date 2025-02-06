from rest_framework import serializers
from .models import Employee, Department, EmployeeDocument, Performance

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'

class PerformanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Performance
        fields = '__all__'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name}" if obj.reviewer else None

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    performance_records = PerformanceSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'user': {'write_only': True}
        }

    def create(self, validated_data):
        # Custom create method to handle additional logic if needed
        employee = Employee.objects.create(**validated_data)
        return employee

    def update(self, instance, validated_data):
        # Custom update method to handle specific update logic
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        # Add more fields as needed
        instance.save()
        return instance
