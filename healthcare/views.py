from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from .models import Department, Doctor, DoctorAvailability, Appointment
from .serializers import DepartmentSerializer, DoctorSerializer, DoctorAvailabilitySerializer, AppointmentSerializer
from django_filters.rest_framework import DjangoFilterBackend

class DepartmentListAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]

class DoctorListAPIView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department']

class DoctorDetailAPIView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

class DoctorAvailabilityListAPIView(generics.ListAPIView):
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        # Only return slots that are not booked
        return DoctorAvailability.objects.filter(doctor_id=doctor_id, is_booked=False)

class AppointmentCreateAPIView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        availability_id = request.data.get('availability')
        
        try:
            with transaction.atomic():
                availability = DoctorAvailability.objects.select_for_update().get(id=availability_id)
                
                if availability.is_booked:
                    return Response({'error': 'This slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark as booked
                availability.is_booked = True
                availability.save()
                
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(
                    patient=request.user,
                    doctor=availability.doctor,
                    availability=availability
                )
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                
        except DoctorAvailability.DoesNotExist:
            return Response({'error': 'Invalid slot selected.'}, status=status.HTTP_400_BAD_REQUEST)

class AppointmentListAPIView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only the appointments belonging to the logged-in user
        return Appointment.objects.filter(patient=self.request.user).order_by('availability__date', 'availability__start_time')

class AppointmentCancelAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)

    def perform_destroy(self, instance):
        with transaction.atomic():
            # Release the slot availability
            availability = instance.availability
            availability.is_booked = False
            availability.save()
            
            # Delete the appointment
            instance.delete()

