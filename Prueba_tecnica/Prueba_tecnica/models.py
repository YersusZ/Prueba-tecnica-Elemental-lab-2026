from django.db import models

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=[
        ('VIP', 'VIP'),
        ('Regular', 'Regular'),
    ])

    class Meta:
        db_table = 'customer'

class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='dates')
    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()

    class Meta:
        db_table = 'appointment'
