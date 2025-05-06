from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
import uuid
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
import json
import logging

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text=_('Required. 3-30 characters. Letters, digits and @/./+/-/_ only.'),
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    total_points = models.IntegerField(default=0)
    quizzes_taken = models.IntegerField(default=0)
    quizzes_created = models.IntegerField(default=0)
    achievements = models.ManyToManyField('Achievement', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_stats(self):
        self.quizzes_taken = self.user.quizattempt_set.filter(completed=True).count()
        self.total_points = self.user.quizattempt_set.filter(completed=True).aggregate(
            total=models.Sum('score'))['total'] or 0
        self.quizzes_created = self.user.quiz_set.count()
        self.save()

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Font Awesome icon class
    points_required = models.IntegerField()
    quizzes_required = models.IntegerField()

    def __str__(self):
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, default='General')
    difficulty = models.CharField(max_length=20, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    time_limit = models.IntegerField(null=True, blank=True, help_text="Time limit in minutes")
    passing_score = models.IntegerField(default=60, help_text="Minimum score to pass (%)")
    
    def __str__(self):
        return self.title
        
    def get_attempts(self):
        """Get all attempts for this quiz, both AI and custom."""
        logger = logging.getLogger(__name__)
        logger.info(f"Getting attempts for quiz id={self.id}, title={self.title}")
        
        attempts = []
        
        # Get AI quiz attempts - first by exact ID match
        try:
            # Ensure the ID is properly converted to string for comparison
            quiz_id_str = str(self.id)
            logger.info(f"Looking for AI attempts with quiz_id={quiz_id_str}")
            
            # First look for direct ID matches
            ai_attempts = AIQuizAttempt.objects.filter(
                quiz_id=quiz_id_str,
                completed=True
            ).order_by('-completed_at')
            
            logger.info(f"Found {ai_attempts.count()} AI attempts with direct ID match")
            
            # Then look for title matches - but only if we don't have direct matches
            title_match_attempts = []
            if ai_attempts.count() == 0:
                # Use case-insensitive contains for better matching
                title_match_attempts = AIQuizAttempt.objects.filter(
                    quiz_title__icontains=self.title,
                    completed=True
                ).order_by('-completed_at')
                logger.info(f"Found {len(title_match_attempts)} additional AI attempts with title match")
                
                # Auto-fix: Update quiz_id for title matches
                for attempt in title_match_attempts:
                    if not attempt.quiz_id or attempt.quiz_id == 'None' or str(attempt.quiz_id) != quiz_id_str:
                        logger.info(f"Updating quiz_id for attempt {attempt.id} from '{attempt.quiz_id}' to '{quiz_id_str}'")
                        attempt.quiz_id = quiz_id_str
                        attempt.save()
            
            # Get custom quiz attempts
            custom_attempts = QuizAttempt.objects.filter(
                quiz=self,
                completed=True
            ).order_by('-completed_at')
            
            logger.info(f"Found {custom_attempts.count()} custom attempts")
            
            # Combine and format attempts
            for attempt in ai_attempts:
                attempts.append({
                    'type': 'ai',
                    'date': attempt.completed_at,
                    'score': attempt.score,
                    'max_score': attempt.max_score or self.questions.count(),
                    'percentage': attempt.percentage,
                    'time_taken': attempt.time_taken,
                    'attempt_data': attempt.attempt_data if hasattr(attempt, 'attempt_data') else {}
                })
            
            for attempt in title_match_attempts:
                attempts.append({
                    'type': 'ai',
                    'date': attempt.completed_at,
                    'score': attempt.score,
                    'max_score': attempt.max_score or self.questions.count(),
                    'percentage': attempt.percentage,
                    'time_taken': attempt.time_taken,
                    'attempt_data': attempt.attempt_data if hasattr(attempt, 'attempt_data') else {}
                })
            
            for attempt in custom_attempts:
                attempts.append({
                    'type': 'custom',
                    'date': attempt.completed_at,
                    'score': attempt.score,
                    'max_score': self.questions.count(),
                    'percentage': (attempt.score / self.questions.count() * 100) if self.questions.count() > 0 else 0,
                    'time_taken': attempt.completed_at - attempt.started_at if attempt.completed_at and attempt.started_at else None
                })
            
            logger.info(f"Total combined attempts: {len(attempts)}")
            
            # Sort attempts by date (newest first)
            attempts.sort(key=lambda x: x['date'] if x['date'] else timezone.now(), reverse=True)
            
            return attempts
            
        except Exception as e:
            logger.error(f"Error getting attempts: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    points = models.IntegerField(default=1)
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class QuizAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    passed = models.BooleanField(default=False)
    is_challenge = models.BooleanField(default=False)  # Flag to mark challenge attempts
    challenge = models.ForeignKey('Challenge', on_delete=models.SET_NULL, null=True, blank=True, related_name='attempts')  # Link to the challenge

    class Meta:
        unique_together = ['user', 'quiz']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"

class AIQuizAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_quiz_attempts')
    quiz_id = models.CharField(max_length=50)  # Store the AIQuiz id
    quiz_title = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    attempt_data = models.JSONField(default=dict, blank=True)  # Store detailed attempt data
    
    class Meta:
        ordering = ['-completed_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.quiz_title}"
        
    def save(self, *args, **kwargs):
        if self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100
        super().save(*args, **kwargs)
        
        # Update user profile statistics
        if self.completed and hasattr(self.user, 'profile'):
            profile = self.user.profile
            profile.quizzes_taken = profile.quizzes_taken + 1
            profile.total_points = profile.total_points + self.score
            profile.save()

class Challenge(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('declined', 'Declined')
    ]
    
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_challenges')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_challenges')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} challenged {self.receiver.username} - {self.quiz.title}"

class SSQuizAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ss_quiz_attempts')
    quiz_title = models.CharField(max_length=200)
    quiz_data = models.JSONField(default=dict)  # Store the complete quiz data
    user_answers = models.JSONField(default=dict)  # Store user's answers
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-completed_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.quiz_title}"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update user profile statistics
        if self.completed and hasattr(self.user, 'profile'):
            profile = self.user.profile
            profile.quizzes_taken = profile.quizzes_taken + 1
            profile.total_points = profile.total_points + self.score
            profile.save()

