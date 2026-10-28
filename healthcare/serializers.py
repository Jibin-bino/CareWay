from rest_framework import serializers
from .models import Department, Doctor, DoctorAvailability, Appointment

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'

class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_department = serializers.CharField(source='doctor.department.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    doctor_fee = serializers.DecimalField(source='doctor.fee', max_digits=10, decimal_places=2, read_only=True)
    date = serializers.DateField(source='availability.date', read_only=True)
    start_time = serializers.TimeField(source='availability.start_time', read_only=True)
    end_time = serializers.TimeField(source='availability.end_time', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['patient', 'doctor', 'created_at']
