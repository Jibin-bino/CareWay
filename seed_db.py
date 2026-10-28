import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from healthcare.models import Department, Doctor, DoctorAvailability

def seed_data():
    departments = [
        "General Medicine", "Cardiology", "Dermatology",
        "Neurology", "Orthopedics", "Pediatrics", "Gynecology"
    ]
    
    dept_objs = {}
    for dept in departments:
        d, _ = Department.objects.get_or_create(name=dept, description=f"Department of {dept}")
        dept_objs[dept] = d

    doctors = [
        {"name": "Alice Smith", "dept": "General Medicine", "spec": "General Physician", "exp": 10, "fee": 500},
        {"name": "Bob Johnson", "dept": "General Medicine", "spec": "Internal Medicine", "exp": 15, "fee": 600},
        {"name": "Carol Williams", "dept": "Cardiology", "spec": "Cardiologist", "exp": 12, "fee": 1000},
        {"name": "David Brown", "dept": "Cardiology", "spec": "Interventional Cardiologist", "exp": 8, "fee": 900},
        {"name": "Eve Davis", "dept": "Dermatology", "spec": "Dermatologist", "exp": 5, "fee": 750},
        {"name": "Frank Miller", "dept": "Neurology", "spec": "Neurologist", "exp": 20, "fee": 1200},
        {"name": "Grace Wilson", "dept": "Orthopedics", "spec": "Orthopedic Surgeon", "exp": 18, "fee": 1100},
        {"name": "Henry Moore", "dept": "Pediatrics", "spec": "Pediatrician", "exp": 11, "fee": 650},
        {"name": "Ivy Taylor", "dept": "Gynecology", "spec": "Gynecologist", "exp": 14, "fee": 850},
    ]

    for doc_data in doctors:
        doc, _ = Doctor.objects.get_or_create(
            name=doc_data["name"],
            department=dept_objs[doc_data["dept"]],
            specialization=doc_data["spec"],
            experience_years=doc_data["exp"],
            fee=doc_data["fee"]
        )

        # Create availability slots for the next 3 days
        if not DoctorAvailability.objects.filter(doctor=doc).exists():
            for i in range(3):
                avail_date = date.today() + timedelta(days=i)
                DoctorAvailability.objects.create(doctor=doc, date=avail_date, start_time="09:00", end_time="10:00")
                DoctorAvailability.objects.create(doctor=doc, date=avail_date, start_time="10:00", end_time="11:00")
                DoctorAvailability.objects.create(doctor=doc, date=avail_date, start_time="11:00", end_time="12:00")

if __name__ == '__main__':
    seed_data()
    print("Database seeded successfully.")
