from datetime import timedelta
from django.utils import timezone

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 5
 
RATE_THRESHOLD = 10
RATE_WINDOW_SECONDS = 60


def is_suspicious(ip_address: str) -> bool:
    """
    Return True if the given IP triggers any detection rule.
    Import is deferred to avoid circular imports at module load time.
    """
    from .models import LoginEvent

    now = timezone.now()
    
    # RULE 1: Brute force detection
    brute_window = now - timedelta(minutes=BRUTE_FORCE_WINDOW_MINUTES)
    failed_count = LoginEvent.objects.filter(
        ip_address=ip_address,
        success=False,
        timestamp__gte=brute_window,
    ).count()
    
    if failed_count > BRUTE_FORCE_THRESHOLD:
        return True

    # RULE 2: Rate-abuse detection
    rate_window = now - timedelta(seconds=RATE_WINDOW_SECONDS)
    rate_count = LoginEvent.objects.filter(
        ip_address=ip_address,
        timestamp__gte=rate_window
    ).count()
    
    if rate_count > RATE_THRESHOLD:
        return True

    return False