from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('customquiz/', views.custom_quiz, name='custom_quiz'),
    path('createownquiz/', views.create_own_quiz, name='create_own_quiz'),
    path('api/save-custom-quiz/', views.save_custom_quiz, name='save_custom_quiz'),
    path('api/save-create-own-quiz/', views.save_create_own_quiz, name='save_create_own_quiz'),
]