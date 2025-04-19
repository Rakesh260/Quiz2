from datetime import datetime, timedelta

from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404
from .models import Department, Employee, Attendance, Performance, LeaveRecord
from .serializers import (
    DepartmentSerializer, EmployeeSerializer,
    AttendanceSerializer, PerformanceSerializer,
    LeaveRecordSerializer, UserSerializer
)
from django.shortcuts import render

from django.contrib.auth import authenticate
import json
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, ScopedRateThrottle


class RegisterUserView(APIView):
    permission_classes = []
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'register'

    """Register a new user"""
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeVisualizationAPI(APIView):
    """Endpoint to provide data for visualizations"""

    def get(self, request):
        # Department stats
        departments = Department.objects.annotate(
            employee_count=Count('employees'),
            avg_salary=Avg('employees__salary')
        ).values('name', 'employee_count', 'avg_salary')

        # Attendance (last 30 days)
        date_threshold = datetime.now() - timedelta(days=30)
        attendance = Attendance.objects.filter(
            date__gte=date_threshold
        ).values('status').annotate(
            count=Count('id')
        )

        # Performance data
        performance = Performance.objects.values(
            'employee__department__name'
        ).annotate(
            avg_score=Avg('score')
        )

        return Response({
            'departments': list(departments),
            'attendance': list(attendance),
            'performance': list(performance)
        })


class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT Authentication API"""
    permission_classes = []
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):

        response = super().post(request, *args, **kwargs)
        username = request.data.get('username')
        user = authenticate(username=username, password=request.data.get('password'))

        if user:
            user_data = UserSerializer(user).data
            return Response({
                "access": response.data['access'],
                "refresh": response.data['refresh'],
                "user": json.dumps(user_data)
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class DepartmentAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_object(self, pk):
        return get_object_or_404(Department, pk=pk)

    def get(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    def put(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        department = self.get_object(pk)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]

    def get(self, request):
        employees = Employee.objects.select_related('department')
        department_id = request.query_params.get('department_id')
        if department_id:
            employees = employees.filter(department_id=department_id)

        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]

    def get_object(self, pk):
        return get_object_or_404(Employee.objects.select_related('department'), pk=pk)

    def get(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttendanceAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        attendances = Attendance.objects.select_related('employee')
        employee_id = request.query_params.get('employee_id')
        date = request.query_params.get('date')
        status = request.query_params.get('status')

        if employee_id:
            attendances = attendances.filter(employee_id=employee_id)
        if date:
            attendances = attendances.filter(date=date)
        if status:
            attendances = attendances.filter(status=status)

        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_object(self, pk):
        return get_object_or_404(Attendance.objects.select_related('employee'), pk=pk)

    def get(self, request, pk):
        attendance = self.get_object(pk)
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)

    def put(self, request, pk):
        attendance = self.get_object(pk)
        serializer = AttendanceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        attendance = self.get_object(pk)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeePerformanceAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'high_volume'

    def get(self, request, employee_id):
        performances = Performance.objects.filter(employee_id=employee_id)
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data)

    def post(self, request, employee_id):
        data = request.data.copy()
        data['employee'] = employee_id
        serializer = PerformanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeAttendanceSummaryAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'high_volume'

    def get(self, request, employee_id):
        from django.db.models import Count, Q
        from datetime import date, timedelta

        employee = get_object_or_404(Employee, pk=employee_id)
        today = date.today()
        last_30_days = today - timedelta(days=30)

        attendance_data = Attendance.objects.filter(
            employee_id=employee_id,
            date__gte=last_30_days
        ).aggregate(
            present=Count('id', filter=Q(status='P')),
            absent=Count('id', filter=Q(status='A')),
            late=Count('id', filter=Q(status='L')),
            half_day=Count('id', filter=Q(status='H'))
        )

        avg_performance = Performance.objects.filter(
            employee_id=employee_id
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0

        response_data = {
            'employee': EmployeeSerializer(employee).data,
            'attendance_summary': attendance_data,
            'average_performance': round(avg_performance, 2),
            'performance_rating': Performance.RATING_CHOICES[int(round(avg_performance)) - 1][
                1] if avg_performance else None
        }

        return Response(response_data)


def analytics_dashboard(request):

    return render(request, 'analytics.html')

