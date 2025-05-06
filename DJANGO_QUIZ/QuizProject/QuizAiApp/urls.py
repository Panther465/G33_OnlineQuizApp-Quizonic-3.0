from django.urls import path
from . import views

app_name = 'quizai'

urlpatterns = [
    path('', views.index, name='index'),  # Empty path to match /quizai/
    path('index/', views.index, name='index_alt'),
    path('generate/', views.generate_quiz, name='generate'),
    path('edit/', views.edit_quiz, name='edit'),
    path('start/', views.start_quiz, name='start_quiz'),
    path('next_question/', views.next_question, name='next_question'),
    path('finish/', views.finish_quiz, name='finish_quiz'),
    path('download/', views.download_quiz, name='download_quiz'),
    path('check_media/', views.check_media_access, name='check_media'),
    # Add other routes that correspond to your Flask routes
] 