from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Avg

from .models import SalaryComponent, PayrollPeriod, Payslip
from .serializers import SalaryComponentSerializer, PayrollPeriodSerializer, PayslipSerializer

# Create your views here.

class SalaryComponentViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Salary Components
    """
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'component_type']
    ordering_fields = ['percentage']

class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Payroll Periods
    """
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_processed']
    ordering_fields = ['start_date', 'end_date']

    @action(detail=True, methods=['post'])
    def process_payroll(self, request, pk=None):
        """
        Process payroll for a specific period
        """
        payroll_period = self.get_object()
        
        if payroll_period.is_processed:
            return Response(
                {"detail": "This payroll period has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Logic to generate payslips for all employees
        # This is a simplified version and would need more complex implementation
        payroll_period.is_processed = True
        payroll_period.processed_at = timezone.now()
        payroll_period.save()
        
        return Response({"detail": "Payroll processed successfully."})

class PayslipViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Payslips
    """
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'payroll_period', 'is_paid']
    ordering_fields = ['net_salary', 'payroll_period__start_date']

    def get_queryset(self):
        """
        Customize queryset based on user role
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Payslip.objects.all()
        return Payslip.objects.filter(employee__user=user)

    @action(detail=False, methods=['get'])
    def salary_statistics(self, request):
        """
        Generate salary statistics
        """
        stats = {
            'total_payroll': Payslip.objects.aggregate(total=Sum('net_salary'))['total'],
            'average_salary': Payslip.objects.aggregate(avg=Avg('net_salary'))['avg'],
            'highest_salary': Payslip.objects.order_by('-net_salary').first().net_salary if Payslip.objects.exists() else 0,
            'lowest_salary': Payslip.objects.order_by('net_salary').first().net_salary if Payslip.objects.exists() else 0
        }
        return Response(stats)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark a payslip as paid
        """
        payslip = self.get_object()
        payslip.is_paid = True
        payslip.payment_date = timezone.now()
        payslip.save()
        
        serializer = self.get_serializer(payslip)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unpaid_payslips(self, request):
        """
        Retrieve all unpaid payslips
        """
        unpaid_payslips = Payslip.objects.filter(is_paid=False)
        serializer = self.get_serializer(unpaid_payslips, many=True)
        return Response(serializer.data)
