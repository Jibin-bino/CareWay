from django.urls import path
from .views import (
    DepartmentListAPIView, 
    DoctorListAPIView, 
    DoctorDetailAPIView, 
    DoctorAvailabilityListAPIView,
    AppointmentCreateAPIView,
    AppointmentListAPIView,
    AppointmentCancelAPIView
)

urlpatterns = [
    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('doctors/', DoctorListAPIView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', DoctorDetailAPIView.as_view(), name='doctor-detail'),
    path('doctors/<int:doctor_id>/availability/', DoctorAvailabilityListAPIView.as_view(), name='doctor-availability'),
    path('appointments/', AppointmentCreateAPIView.as_view(), name='appointment-create'),
    path('appointments/list/', AppointmentListAPIView.as_view(), name='appointment-list'),
    path('appointments/<int:pk>/cancel/', AppointmentCancelAPIView.as_view(), name='appointment-cancel'),
]
