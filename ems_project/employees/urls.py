from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet, EmployeeDocumentViewSet, PerformanceViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='employee-document')
router.register(r'performances', PerformanceViewSet, basename='performance')

urlpatterns = [
    path('', include(router.urls)),
]
