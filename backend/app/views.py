# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import LoginEvent
from .serializers import LoginEventSerializer, LoginAttemptInputSerializer
from .detection import is_suspicious

# Create your views here.
class LoginAttemptView(APIView):
    """
    POST /login-attempt
    Record a login attempt and run detection logic.
    """
    def post(self, request):
        serializer = LoginAttemptInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        # Persist the event first so detection can count it
        event = LoginEvent.objects.create(
            ip_address=data['ip'],
            username=data.get('username', ''),
            success=data['success'],
            is_suspicious=False,
        )

        # Re-evaluation of suspicion (new event included)
        suspicious = is_suspicious(data['ip'])

        if suspicious:
            # Flag ALL events from this IP
            LoginEvent.objects.filter(ip_address=data['ip']).update(is_suspicious=True)
            event.refresh_from_db()
        
        return Response(LoginEventSerializer(event).data, status=status.HTTP_201_CREATED)


class EventListView(APIView):
    """GET /events - all events, newest first"""

    def get(self, request):
        events = LoginEvent.objects.all()
        return Response(LoginEventSerializer(events, many=True).data)


class SuspiciousEventsView(APIView):
    """GET /suspicious - only flagged events"""
    
    def get(self, request):
        events = LoginEvent.objects.filter(is_suspicious=True)
        return Response(LoginEventSerializer(events, many=True).data)


class StatsView(APIView):
    """GET /stats - aggregate counts for the dashboard"""

    def get(self, request):
        total = LoginEvent.objects.count()
        failed = LoginEvent.objects.filter(success=False).count()
        succeeded = LoginEvent.objects.filter(success=True).count()
        suspicious = LoginEvent.objects.filter(is_suspicious=True).count()
        
        return Response({
            'total': total,
            'failed': failed,
            'succeeded': succeeded,
            'suspicious': suspicious,
        })