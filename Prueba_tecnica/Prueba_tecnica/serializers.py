from datetime import datetime, timedelta, time

from rest_framework import serializers
from .models import Customer, Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        customer = data.get('customer')
        date = data.get('date')
        start_time = data.get('start_time')
        duration_minutes = data.get('duration_minutes')
        end_time = (datetime.combine(date, start_time) + timedelta(minutes=duration_minutes)).time()

        if not customer or not date or not start_time or not duration_minutes:
            raise serializers.ValidationError("All fields are required.")

        if customer and customer.category == 'VIP':
            start_time = (datetime.combine(date, start_time) - timedelta(minutes=15)).time()
            end_time = (datetime.combine(date, end_time) + timedelta(minutes=15)).time()


        if (start_time < time(14, 0) and end_time > time(13, 0)):
            raise serializers.ValidationError("Appointments cannot be scheduled during the lunch break (1:00 PM to 2:00 PM).")
            
        if date.weekday() == 1 and (start_time >= time(16, 0) or end_time > time(16, 0)):
            raise serializers.ValidationError("Appointments cannot be scheduled on Tuesdays after 4:00 PM.")
        
        if datetime.combine(date, start_time) < datetime.now():
            raise serializers.ValidationError("Appointments cannot be scheduled in the past.")
        
        overlapping_appointments = Appointment.objects.filter(
            date=date,
        )
        for appointment in overlapping_appointments:
            existing_start = appointment.start_time
            existing_end = (datetime.combine(date, existing_start) + timedelta(minutes=appointment.duration_minutes)).time()
            if (start_time < existing_end and end_time > existing_start):
                raise serializers.ValidationError("This appointment overlaps with an existing appointment.")
            
        return data

class AppointmentAvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()

    def validate(self, value):
        date = value.get('date')
        if not date:
            raise serializers.ValidationError("Date is required.")
        
        if date < datetime.now().date():
            raise serializers.ValidationError("The date cannot be in the past.")        
        return value

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
