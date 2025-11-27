import secrets
from django.db import models
from django.utils import timezone

class QuickPrompt(models.Model):
  title = models.CharField(max_length=255)
  prompt = models.TextField()
  is_public = models.BooleanField(default=False)
  
  def __str__(self):
    return self.title

class AuthToken(models.Model):
    user = models.CharField(max_length=50, unique=True)
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def regenerate(self):
        self.key = secrets.token_hex(32)  # 64-char token
        self.save()

    def __str__(self):
        return f"Token for {self.user}"

    @staticmethod
    def create_token(user):
        token, created = AuthToken.objects.get_or_create(user=user)
        if created or not token.key:
            token.key = secrets.token_hex(32)
            token.save()
        return token
        
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

class PromptLog(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    # Optional: which AI model generated the response
    model_used = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} @ {self.created_at}"

class RequestLog(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        username = self.user.username if self.user else "guest"
        return f"{username} - {self.date} ({self.count} requests)"

class AISetting(models.Model):
    huggingface_token = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    limit_per_day = models.IntegerField(default=10)
    system_prompt = models.TextField()
    research_exp = models.BooleanField(default=False)

    def __str__(self):
        return self.model_name