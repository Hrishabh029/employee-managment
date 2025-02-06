from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count

from .models import Attendance, LeaveRequest
from .serializers import AttendanceSerializer, LeaveRequestSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Attendance records
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'status']
    ordering_fields = ['date']

    def get_queryset(self):
        """
        Optionally filter attendance by date range
        """
        queryset = Attendance.objects.all()
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        return queryset

    @action(detail=False, methods=['get'])
    def today_attendance(self, request):
        """
        Retrieve today's attendance records
        """
        today = timezone.now().date()
        today_attendance = Attendance.objects.filter(date=today)
        serializer = self.get_serializer(today_attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Generate monthly attendance summary
        """
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        attendance_summary = Attendance.objects.filter(
            date__year=year, 
            date__month=month
        ).values('employee', 'status').annotate(count=Count('status'))
        
        return Response(attendance_summary)

class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Leave Requests
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    ordering_fields = ['start_date']

    def get_queryset(self):
        """
        Customize queryset based on user role
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee__user=user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def approve_leave(self, request, pk=None):
        """
        Approve a leave request
        """
        leave_request = self.get_object()
        leave_request.status = 'A'  # Approved
        leave_request.approved_by = request.user.employee_profile
        leave_request.approved_on = timezone.now()
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def reject_leave(self, request, pk=None):
        """
        Reject a leave request
        """
        leave_request = self.get_object()
        leave_request.status = 'R'  # Rejected
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_requests(self, request):
        """
        Retrieve all pending leave requests
        """
        pending_requests = LeaveRequest.objects.filter(status='P')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
