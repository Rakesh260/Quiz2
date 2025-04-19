
from django.urls import path
from .views import (
    DepartmentAPI, DepartmentDetailAPI,
    EmployeeAPI, EmployeeDetailAPI,
    AttendanceAPI, AttendanceDetailAPI,
    EmployeePerformanceAPI, EmployeeAttendanceSummaryAPI, RegisterUserView, CustomTokenObtainPairView,
    EmployeeVisualizationAPI, analytics_dashboard
)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),

    path('departments/', DepartmentAPI.as_view(), name='department-list'),
    path('departments/<int:pk>/', DepartmentDetailAPI.as_view(), name='department-detail'),

    path('employees/', EmployeeAPI.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailAPI.as_view(),  name='employee-detail'),

    path('attendances/', AttendanceAPI.as_view(), name='attendance-list'),
    path('attendances/<int:pk>/', AttendanceDetailAPI.as_view(), name='attendance-detail'),

    path('employees/<int:employee_id>/performances/', EmployeePerformanceAPI.as_view(),  name='performance-list'),
    path('employees/<int:employee_id>/performances/create/', EmployeePerformanceAPI.as_view(), name='performance-create'),

    path('employees/<int:employee_id>/attendance-summary/', EmployeeAttendanceSummaryAPI.as_view(), name='attendance-summary'),

    path('visualization/', EmployeeVisualizationAPI.as_view(), name='viz-data'),
    path('analytics/', analytics_dashboard, name='analytics'),

]
