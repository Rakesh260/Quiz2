# Generated by Django 4.2.20 on 2025-04-15 04:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('location', models.CharField(max_length=100)),
                ('budget', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('established_date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Departments',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('address', models.TextField(blank=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('position', models.CharField(max_length=100)),
                ('join_date', models.DateField()),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_manager', models.BooleanField(default=False)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='employee_photos/')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employeeapp.department')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(choices=[(1, 'Poor'), (2, 'Needs Improvement'), (3, 'Meets Expectations'), (4, 'Exceeds Expectations'), (5, 'Outstanding')])),
                ('review_date', models.DateField(auto_now_add=True)),
                ('next_review_date', models.DateField()),
                ('strengths', models.TextField()),
                ('areas_for_improvement', models.TextField()),
                ('remarks', models.TextField(blank=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='employeeapp.employee')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews_given', to='employeeapp.employee')),
            ],
            options={
                'verbose_name_plural': 'Performance Reviews',
                'ordering': ['-review_date'],
            },
        ),
        migrations.CreateModel(
            name='LeaveRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('AL', 'Annual Leave'), ('SL', 'Sick Leave'), ('ML', 'Maternity Leave'), ('PL', 'Paternity Leave'), ('CL', 'Compassionate Leave'), ('UL', 'Unpaid Leave')], max_length=2)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('days', models.PositiveIntegerField(editable=False)),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected'), ('C', 'Cancelled')], default='P', max_length=1)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leaves_approved', to='employeeapp.employee')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='employeeapp.employee')),
            ],
            options={
                'verbose_name_plural': 'Leave Records',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('check_in', models.TimeField(blank=True, null=True)),
                ('check_out', models.TimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('P', 'Present'), ('A', 'Absent'), ('L', 'Late'), ('H', 'Half Day'), ('V', 'Vacation')], default='P', max_length=1)),
                ('notes', models.TextField(blank=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='employeeapp.employee')),
            ],
            options={
                'verbose_name_plural': 'Attendance Records',
                'ordering': ['-date', 'employee'],
            },
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['name'], name='employeeapp_name_f1c62a_idx'),
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['department'], name='employeeapp_departm_85fb1f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('employee', 'date')},
        ),
    ]
