from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalaryComponentViewSet, PayrollPeriodViewSet, PayslipViewSet

router = DefaultRouter()
router.register(r'salary-components', SalaryComponentViewSet, basename='salary-component')
router.register(r'payroll-periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'payslips', PayslipViewSet, basename='payslip')

urlpatterns = [
    path('', include(router.urls)),
]
