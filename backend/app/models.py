from django.db import models

# Create your models here.
class LoginEvent(models.Model):
    ip_address = models.CharField(max_length=45)
    timestamp = models.DateTimeField(auto_now_add=False, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.timestamp is None:
            from django.utils import timezone
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)
    
    success = models.BooleanField(default=False)
    username = models.CharField(max_length=150, blank=True, null=True)
    is_suspicious = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        if self.success:
            status = 'SUCCESS'
        else:
            status = 'FAIL'
        
        if self.is_suspicious:
            flag = ' [SUSPICIOUS]'
        else:
            flag = ''
        
        return f"[{self.timestamp}] {self.ip_address} - {status}{flag}"
