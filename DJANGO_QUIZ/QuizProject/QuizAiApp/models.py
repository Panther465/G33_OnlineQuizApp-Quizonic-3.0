from django.db import models
from django.conf import settings

# Create your models here.

class AIQuiz(models.Model):
    """Model to store AI-generated quizzes"""
    title = models.CharField(max_length=200)
    questions_json = models.TextField()  # Store quiz questions as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class QuizResult(models.Model):
    quiz = models.ForeignKey(AIQuiz, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')
    score = models.IntegerField()
    max_score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(help_text="Time taken in seconds")
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}/{self.max_score}"
        
    @property
    def percentage_score(self):
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0

class TobbiAPIConfig(models.Model):
    """Model to store TOBBI API configuration"""
    api_key = models.CharField(max_length=255, help_text="API key for TOBBI API access")
    base_url = models.URLField(default="https://openrouter.ai/api/v1", 
                               help_text="Base URL for the API")
    model = models.CharField(max_length=100, default="deepseek/deepseek-r1:free", 
                             help_text="AI model to use")
    is_active = models.BooleanField(default=True, help_text="Whether this configuration is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "TOBBI API Configuration"
        verbose_name_plural = "TOBBI API Configurations"
    
    def __str__(self):
        return f"TOBBI API Config ({self.model})"
    
    def save(self, *args, **kwargs):
        # Ensure only one active configuration
        if self.is_active:
            TobbiAPIConfig.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
