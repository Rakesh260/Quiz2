
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from faker import Faker
from employeeapp.models import Department, Employee, Attendance, Performance, LeaveRecord

fake = Faker()


class Command(BaseCommand):
    help = 'Generates synthetic employee data with unique department names'

    def handle(self, *args, **options):
        self.stdout.write("Starting data generation with unique constraints...")

        department_names = set()
        departments = []

        while len(departments) < 3:
            name = f"{fake.unique.company_suffix()} Department"
            if name not in department_names:
                dept = Department.objects.create(
                    name=name,
                    location=fake.city(),
                    budget=random.randint(100000, 1000000),
                    established_date=fake.date_between(start_date='-10y', end_date='-1y'),
                    active=random.choice([True, False])
                )
                departments.append(dept)
                department_names.add(name)
                self.stdout.write(f"Created department: {dept}")

        employees = []
        manager_count = 0

        for i in range(5):
            is_manager = False
            if manager_count < len(departments):
                is_manager = True
                manager_count += 1

            while True:
                email = fake.email()
                if not Employee.objects.filter(email=email).exists():
                    break

            emp = Employee.objects.create(
                name=fake.unique.name(),
                email=email,
                phone=fake.unique.phone_number()[:15],
                address=fake.address(),
                gender=random.choice(['M', 'F', 'O']),
                department=departments[manager_count - 1] if is_manager else random.choice(departments),
                position=fake.job(),
                join_date=fake.date_between(start_date='-5y', end_date='today'),
                salary=random.randint(30000, 120000),
                is_manager=is_manager
            )
            employees.append(emp)
            self.stdout.write(f"Created employee: {emp} (Manager: {is_manager})")

        status_choices = ['P', 'A', 'L', 'H', 'V']
        status_weights = [8, 1, 2, 1, 1]

        for emp in employees:
            for day in range(30):
                date = datetime.now().date() - timedelta(days=day)

                if date.weekday() >= 5:
                    continue

                status = random.choices(status_choices, weights=status_weights, k=1)[0]

                check_in = None
                check_out = None

                if status == 'P':
                    check_in = datetime.strptime(f"{random.randint(8, 9)}:{random.randint(0, 59):02d}", "%H:%M").time()
                    check_out = datetime.strptime(f"{random.randint(16, 18)}:{random.randint(0, 59):02d}",
                                                  "%H:%M").time()
                elif status == 'L':  # Late
                    check_in = datetime.strptime(f"{random.randint(10, 12)}:{random.randint(0, 59):02d}",
                                                 "%H:%M").time()
                    check_out = datetime.strptime(f"{random.randint(17, 19)}:{random.randint(0, 59):02d}",
                                                  "%H:%M").time()

                if not Attendance.objects.filter(employee=emp, date=date).exists():
                    Attendance.objects.create(
                        employee=emp,
                        date=date,
                        check_in=check_in,
                        check_out=check_out if status in ['P', 'L'] else None,
                        status=status,
                        notes=fake.sentence() if random.random() < 0.3 else ""
                    )
        for emp in employees:
            for _ in range(random.randint(1, 3)):

                reviewer = random.choice(
                    [e for e in employees if e.is_manager and e.department == emp.department]
                ) if any(e.is_manager and e.department == emp.department for e in employees) else None

                review_date = fake.date_between(
                    start_date=emp.join_date,
                    end_date='today'
                )

                while Performance.objects.filter(employee=emp, review_date=review_date).exists():
                    review_date = review_date + timedelta(days=1)

                Performance.objects.create(
                    employee=emp,
                    reviewer=reviewer,
                    score=random.randint(1, 5),
                    review_date=review_date,
                    next_review_date=review_date + timedelta(days=365),
                    strengths=fake.paragraph(),
                    areas_for_improvement=fake.paragraph(),
                    remarks=fake.paragraph() if random.random() < 0.7 else ""
                )

        leave_types = [lt[0] for lt in LeaveRecord.LEAVE_TYPES]

        for emp in employees:
            for _ in range(random.randint(1, 2)):
                start_date = fake.date_between(start_date='-6m', end_date='+1m')
                end_date = start_date + timedelta(days=random.randint(1, 14))

                approver = random.choice(
                    [e for e in employees if e.is_manager and e.department == emp.department]
                ) if any(e.is_manager and e.department == emp.department for e in employees) else None

                status = 'A' if approver else random.choice(['P', 'R'])

                LeaveRecord.objects.create(
                    employee=emp,
                    leave_type=random.choice(leave_types),
                    start_date=start_date,
                    end_date=end_date,
                    reason=fake.sentence(),
                    status=status,
                    approved_by=approver if status == 'A' else None,
                    approved_date=datetime.now() if status == 'A' else None
                )

        self.stdout.write(self.style.SUCCESS(f"""
        Successfully generated synthetic data with all constraints!
        - Departments: {len(departments)} (all unique names)
        - Employees: {len(employees)} (Managers: {manager_count}, all unique emails)
        - Attendance records: ~{Attendance.objects.count()}
        - Performance reviews: ~{Performance.objects.count()}
        - Leave records: ~{LeaveRecord.objects.count()}
        """))
