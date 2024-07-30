from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from firebase_admin import messaging
from django.shortcuts import render

from .models import User, Flight, Notification
from .serializers import UserSerializer, FlightSerializer, RegisterSerializer, LoginSerializer, NotificationSerializer

# Utility functions for sending notifications
def send_notification(registration_ids, message_title, message_desc):
    messages = []
    for token in registration_ids:
        message = messaging.Message(
            notification=messaging.Notification(
                title=message_title,
                body=message_desc,
            ),
            token=token,
        )
        messages.append(message)

    try:
        batch_response = messaging.send_all(messages)
        print(f'{batch_response.success_count} messages were sent successfully')
    except Exception as e:
        print(f"Error sending FCM notification: {str(e)}")

def send_email_notification(email, subject, message):
    try:
        send_mail(
            subject,
            message,
            'siddhartadhikari84@gmail.com',
            [email],
            fail_silently=False,
        )
        print(f"Email sent successfully to {email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def send_sms_notification(phone_number, message):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent successfully: {message.sid}")
    except TwilioRestException as e:
        print(f"Error sending SMS: {str(e)}")

def index(request):
    return render(request, 'index.html')
# http://127.0.0.1:8000/register/ (POST)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# http://127.0.0.1:8000/login/ (POST)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# http://127.0.0.1:8000/logout/ (POST)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    # URL: http://127.0.0.1:8000/flights/
    # URL: http://127.0.0.1:8000/flights/{id}/
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(self.request, instance)
        
        # Fetch real-time updates
        flight_data = self.get_real_time_flight_data(instance.flight_number)
        serializer = self.get_serializer(instance)
        
        # Merge the real-time data with the serialized data
        
        # Serialize data
        serializer = self.get_serializer(instance)
        response_data = serializer.data
        
        return Response(response_data)
        
    # http://127.0.0.1:8000/flights/real-time/{flight_number}/
    def get_real_time_flight_data(self, flight_number):
        try:
            flight = Flight.objects.get(flight_number=flight_number)
            serializer = FlightSerializer(flight)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Flight.DoesNotExist:
            return Response({"error": "Flight not found"}, status=status.HTTP_404_NOT_FOUND)

    # http://127.0.0.1:8000/flights/{id}/ (PUT)
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Send push notifications
        flight = self.get_object()
        self.send_flight_update_notifications(flight)
        
        return response

    def send_flight_update_notifications(self, flight):
        users = User.objects.all()
        for user in users:
            message = f"Flight {flight.flight_number} status updated. New gate: {flight.departure_gate}"
            send_user_notifications(user, message)

def send_user_notifications(user, message):
    if user.fcm_token:
        send_notification([user.fcm_token], 'Flight Status Update', message)
    if user.email:
        send_email_notification(user.email, 'Flight Status Update', message)
    if user.phone_number:
        send_sms_notification(user.phone_number, message)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

# 'http://127.0.0.1:8000/api/notifications/'(POST)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = self.get_object()
        self.send_notifications(instance)
        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        self.send_notifications(instance)

        return Response(serializer.data)

    def send_notifications(self, notification):
        print("Notification",notification)
        message = notification.message
        recipient = notification.recipient

        if notification.method == 'email':
            send_email_notification(recipient.email, 'Flight Status Update', message)
        elif notification.method == 'sms':
            send_sms_notification(recipient.phone_number, message)
        elif notification.method == 'app':
            send_notification([recipient.fcm_token], 'Flight Status Update', message)