from django.db import models
from django.core.validators import MinValueValidator


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    established_date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name} ({self.location})"


class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    position = models.CharField(max_length=100)
    join_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_manager = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.name} - {self.position}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('H', 'Half Day'),
        ('V', 'Vacation'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', 'employee']
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.get_status_display()})"


class Performance(models.Model):
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Needs Improvement'),
        (3, 'Meets Expectations'),
        (4, 'Exceeds Expectations'),
        (5, 'Outstanding'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performances')
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviews_given')
    score = models.IntegerField(choices=RATING_CHOICES)
    review_date = models.DateField(auto_now_add=True)
    next_review_date = models.DateField()
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-review_date']
        verbose_name_plural = "Performance Reviews"

    def __str__(self):
        return f"{self.employee.name} - {self.get_score_display()} ({self.review_date})"


class LeaveRecord(models.Model):
    LEAVE_TYPES = [
        ('AL', 'Annual Leave'),
        ('SL', 'Sick Leave'),
        ('ML', 'Maternity Leave'),
        ('PL', 'Paternity Leave'),
        ('CL', 'Compassionate Leave'),
        ('UL', 'Unpaid Leave'),
    ]

    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('C', 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=2, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.PositiveIntegerField(editable=False)
    reason = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='leaves_approved')
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Leave Records"

    def save(self, *args, **kwargs):

        self.days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"