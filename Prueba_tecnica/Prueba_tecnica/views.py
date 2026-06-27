from datetime import date, datetime, timedelta

from .serializers import CustomerSerializer, AppointmentSerializer, AppointmentAvailabilitySerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Appointment, Customer
from rest_framework import viewsets


class AppointmentAPIView(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @extend_schema(
        request=AppointmentSerializer,
        responses={
            201: OpenApiResponse(response=AppointmentSerializer, description="Appointment created successfully"),
            400: OpenApiResponse(response=AppointmentSerializer, description="Bad Request"),
        },
        description="API endpoint for creating a new appointment. Accepts a POST request with appointment data and returns the created appointment details.",
    )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        customer = validated_data.get('customer')

        if customer.category == 'VIP':
            start_time = validated_data['start_time']
            date = validated_data['date']
            new_start = (datetime.combine(date, start_time) - timedelta(minutes=15)).time()
            serializer.save(
                start_time=new_start,
                duration_minutes=validated_data['duration_minutes'] + 30
            )
        else:
            serializer.save()

    
class AppointmentAvailabilityAPIView(viewsets.ViewSet):
    @extend_schema(
        responses={
            200: OpenApiResponse(response=AppointmentAvailabilitySerializer, description="Available appointments retrieved successfully"),
            400: OpenApiResponse(response=AppointmentAvailabilitySerializer, description="Bad Request"),
        },
        description="API endpoint for retrieving available appointments for a specific date. Accepts a GET request with the date parameter and returns a list of available appointments.",
    )
    def availability(self, request, date):
        serializer = AppointmentAvailabilitySerializer(data={'date': date})
        if serializer.is_valid():
            requested_date = serializer.validated_data['date']
            appointments = Appointment.objects.filter(date=requested_date)
            appointments = list(appointments)
            appointments.append(Appointment(date=requested_date, start_time=datetime.strptime('13:00', '%H:%M').time(), duration_minutes=60))
            if requested_date.weekday() == 1:  # Tuesday
                appointments.append(Appointment(date=requested_date, start_time=datetime.strptime('16:00', '%H:%M').time(), duration_minutes=480))
            return Response(AppointmentSerializer(appointments, many=True).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CustomerAPIView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @extend_schema(
        request=CustomerSerializer,
        responses={
            201: OpenApiResponse(response=CustomerSerializer, description="Customer created successfully"),
            400: OpenApiResponse(response=CustomerSerializer, description="Bad Request"),
        },
        description="API endpoint for creating a new customer. Accepts a POST request with customer data and returns the created customer details.",
    )
    def create(self, request, *args, **kwargs):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    