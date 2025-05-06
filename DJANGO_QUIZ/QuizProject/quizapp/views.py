from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import CustomQuiz, CreateOwnQuiz, Question

def home(request):
    return render(request, 'quizapp/home.html')

def custom_quiz(request):
    return render(request, 'quizapp/customquiz.html')

def create_own_quiz(request):
    return render(request, 'quizapp/createownquiz.html')

@csrf_exempt
@require_POST
def save_custom_quiz(request):
    """API endpoint to save results from API-based quizzes"""
    try:
        data = json.loads(request.body)
        quiz = CustomQuiz(
            quiz_name=data.get('quiz_name'),
            category=data.get('category'),
            difficulty=data.get('difficulty'),
            total_questions=data.get('total_questions'),
            score=data.get('score')
        )
        quiz.save()
        return JsonResponse({'success': True, 'message': 'Quiz results saved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_POST
def save_create_own_quiz(request):
    """API endpoint to save user-created quizzes with all questions and results"""
    try:
        data = json.loads(request.body)
        
        # Create the quiz record
        quiz = CreateOwnQuiz(
            quiz_name=data.get('quiz_name'),
            subject=data.get('subject'),
            total_questions=data.get('total_questions'),
            score=data.get('score')
        )
        quiz.save()
        
        # Save all questions
        questions_data = data.get('questions', [])
        for q_data in questions_data:
            question = Question(
                quiz=quiz,
                question_text=q_data.get('question_text'),
                option1=q_data.get('options')[0],
                option2=q_data.get('options')[1],
                option3=q_data.get('options')[2],
                option4=q_data.get('options')[3],
                correct_answer=q_data.get('correct_answer')
            )
            question.save()
            
        return JsonResponse({'success': True, 'message': 'Quiz and questions saved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
