from django.db import models
import json

class CustomQuiz(models.Model):
    """Model for storing results from API-based quizzes"""
    quiz_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50)
    total_questions = models.IntegerField()
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_name} - {self.score}/{self.total_questions}"

class Question(models.Model):
    """Model for storing individual questions for user-created quizzes"""
    quiz = models.ForeignKey('CreateOwnQuiz', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.IntegerField()  # 0-3 representing the index of the correct option

    def __str__(self):
        return self.question_text[:50]

class CreateOwnQuiz(models.Model):
    """Model for storing user-created quizzes with all questions and results"""
    quiz_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    total_questions = models.IntegerField()
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_name} - {self.score}/{self.total_questions}"
