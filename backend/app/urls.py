from django.urls import path
from .views import LoginAttemptView, EventListView, SuspiciousEventsView, StatsView

urlpatterns = [
    path('login-attempt', LoginAttemptView.as_view(), name='login-attempt'),
    path('events', EventListView.as_view(), name='events'),
    path('suspicious', SuspiciousEventsView.as_view(), name='suspicious'),
    path('stats', StatsView.as_view(), name='stats'),
]