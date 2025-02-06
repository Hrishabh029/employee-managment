from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Employee, Department, EmployeeDocument, Performance
from .serializers import (
    EmployeeSerializer, 
    DepartmentSerializer, 
    EmployeeDocumentSerializer, 
    PerformanceSerializer
)

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Employee records
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'employment_type', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['date_of_joining', 'salary']

    def get_permissions(self):
        """
        Custom permission logic based on action
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def performance_history(self, request, pk=None):
        """
        Retrieve performance history for a specific employee
        """
        employee = self.get_object()
        performances = Performance.objects.filter(employee=employee)
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Retrieve documents for a specific employee
        """
        employee = self.get_object()
        documents = EmployeeDocument.objects.filter(employee=employee)
        serializer = EmployeeDocumentSerializer(documents, many=True)
        return Response(serializer.data)

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Departments
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']

class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Employee Documents
    """
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'document_type']

class PerformanceViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Performance Records
    """
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'review_date']
    search_fields = ['detailed_feedback']
    ordering_fields = ['review_date', 'overall_score']

    def get_queryset(self):
        """
        Optionally filter performances by employee
        """
        queryset = Performance.objects.all()
        employee_id = self.request.query_params.get('employee_id', None)
        if employee_id is not None:
            queryset = queryset.filter(employee_id=employee_id)
        return queryset

    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        """
        Retrieve top performers based on overall score
        """
        top_performers = Performance.objects.order_by('-overall_score')[:10]
        serializer = self.get_serializer(top_performers, many=True)
        return Response(serializer.data)
