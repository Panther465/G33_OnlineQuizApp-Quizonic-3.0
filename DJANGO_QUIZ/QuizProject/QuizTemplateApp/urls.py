from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Authentication URLs
    path('', views.landing_page, name='landing_page'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contactus/', views.contact_view, name='contact'),
    path('help/', views.help_center, name='help_center'),
     path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('qn/', views.qn, name='qn'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('random_quiz/', views.random_quiz, name='random_quiz'),
    
    # Challenge URLs
    path('challenge/<int:challenge_id>/accept/', views.accept_challenge, name='accept_challenge'),
    path('challenge/<int:challenge_id>/decline/', views.decline_challenge, name='decline_challenge'),
    path('challenge/<int:challenge_id>/take/', views.take_challenge, name='take_challenge'),
    
    # Quiz URLs
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('created-quizzes/', views.created_quizzes, name='created_quizzes'),
    path('my-quizzes/', views.my_quizzes, name='my_quizzes'),
    # Add URL for creating quizzes
    path('create-quiz/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/view/', views.view_quiz, name='view_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('question/<int:question_id>/', views.get_question, name='get_question'),







    
] 


