from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import datetime

# Create your models here.

class User(AbstractUser):
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.IntegerField(blank = True, null = True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='flight_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='flight_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name}"

class Flight(models.Model):
    flight_number = models.CharField(max_length=10,default = None)
    departure = models.CharField(max_length=50,default = None)
    destination = models.CharField(max_length=50,default = None)
    departure_gate = models.CharField(max_length=50, default = None)
    arrival_gate = models.CharField(max_length=50,default = None)
    departure_time = models.DateTimeField(default = None)
    arrival_time = models.DateTimeField(default = None)

    def __str__(self):
        return self.flight_number

Type = (
    ('app',"APP"),
    ('sms',"SMS"),
    ('email',"Email")
    )

class Notification(models.Model):
    notification_id = models.IntegerField(primary_key=True,default =0)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null =True, blank = True)
    message = models.CharField(max_length=255,null =True, blank = True)
    timestamp = models.DateTimeField(auto_now_add=True,null =True, blank = True)
    method = models.CharField(max_length=10, choices=Type, null =True, blank = True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null =True, blank = True)

    def __str__(self):
        return f"Notification {self.notification_id} for {self.flight}"




