
from rest_framework import serializers
from .models import Department, Employee, Attendance, Performance, LeaveRecord
from django.db.models import Avg
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(**validated_data)
        return user


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DepartmentStatsSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField()
    avg_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_salary_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    budget_utilization = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    top_performers = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'location', 'budget',
            'employee_count', 'avg_salary', 'total_salary_expense',
            'budget_utilization', 'attendance_rate', 'top_performers'
        ]

    def get_budget_utilization(self, obj):
        if obj.budget and obj.budget > 0:
            return round((obj.total_salary_expense / obj.budget) * 100, 2)
        return 0

    def get_attendance_rate(self, obj):
        from django.db.models import Count, Q
        from datetime import date, timedelta

        thirty_days_ago = date.today() - timedelta(days=30)

        attendance_data = Attendance.objects.filter(
            employee__department=obj,
            date__gte=thirty_days_ago
        ).aggregate(
            present=Count('id', filter=Q(status='P')),
            total=Count('id')
        )

        if attendance_data['total'] > 0:
            return round((attendance_data['present'] / attendance_data['total']) * 100, 2)
        return 0

    def get_top_performers(self, obj):
        top_employees = Employee.objects.filter(
            department=obj
        ).annotate(
            avg_performance=Avg('performances__score')
        ).order_by('-avg_performance')[:3]

        return EmployeeSerializer(top_employees, many=True).data


class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )

    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            'photo': {'required': False}
        }


class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Attendance
        fields = '__all__'


class PerformanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    reviewer = EmployeeSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    score_display = serializers.CharField(source='get_score_display', read_only=True)

    class Meta:
        model = Performance
        fields = '__all__'


class LeaveRecordSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    approved_by = EmployeeSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='approved_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LeaveRecord
        fields = '__all__'
