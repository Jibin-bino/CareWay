from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    specialization = models.CharField(max_length=150)
    bio = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Doctor Availabilities"
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} - {self.date} {self.start_time}-{self.end_time}"

class Appointment(models.Model):
    patient = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    availability = models.OneToOneField(DoctorAvailability, on_delete=models.CASCADE)
    
    patient_name = models.CharField(max_length=150)
    patient_email = models.EmailField()
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.patient_name} with Dr. {self.doctor.name} on {self.availability.date}"

