from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from .models import Quiz, Question, Choice, QuizAttempt, UserProfile, Achievement, AIQuizAttempt, Challenge, CustomUser
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CustomPasswordChangeForm, ChallengeForm
import requests
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

# Flask API URLs
FLASK_API_BASE_URL = 'http://127.0.0.1:5000'
LOGIN_URL = f"http://127.0.0.1:5000/api/login"
REGISTER_URL = f"http://127.0.0.1:5000/api/register"
PROFILE_URL = f"http://127.0.0.1:5000/api/profile"  # Flask API endpoint

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('quiz:home')
    return render(request, 'landingpage.html')

@login_required
def home(request):
    return render(request, 'home.html')

def qn(request):
    return render(request, 'Q&N.html')

def about(request):
    return render(request, 'about.html')

@csrf_exempt
def about_view(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        print(f"Received subscription request - Name: {name}, Email: {email}")  # Debug print
        
        # Prepare data for API
        data = {
            'name': name,
            'email': email
        }
        
        # Make API call to Flask server
        try:
            print("Sending data to Flask API:", data)  # Debug print
            response = requests.post(
                'http://localhost:5000/api/subscribe',  # Replace with your Flask server URL
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print("API Response:", response.status_code, response.text)  # Debug print
            
            if response.status_code == 201:
                # Send confirmation email to the user
                send_mail(
                    subject="Welcome to Quizonic!",
                    message=f"Hi {name},\n\nThank you for subscribing to Quizonic! You'll now receive updates and news about our latest quizzes and features.\n\nHappy quizzing!\nThe Quizonic Team",
                    from_email='recker2060@gmail.com',
                    recipient_list=[email],
                    fail_silently=False,
                )
                return JsonResponse({'message': 'Successfully subscribed! Thank you for joining Quizonic.'})
            else:
                error_data = response.json()
                return JsonResponse(
                    {'error': error_data.get('error', 'Unknown error')},
                    status=400
                )
                
        except requests.exceptions.RequestException as e:
            print("Request error:", str(e))  # Debug print
            return JsonResponse(
                {'error': 'Could not connect to the server'},
                status=500
            )
    
    return render(request, 'about.html')

@login_required
def contact_view(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Prepare data for API
        data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        
        # Make API call to Flask server
        try:
            response = requests.post(
                'http://localhost:5000/api/contact',  # Replace with your Flask server URL
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                # Send email notification
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}",
                    from_email='recker2060@gmail.com',
                    recipient_list=['recker2060@gmail.com'],
                    fail_silently=False,
                )
                return JsonResponse({'message': 'Message sent successfully'})
            else:
                return JsonResponse(
                    {'error': response.json().get('error', 'Unknown error')},
                    status=400
                )
                
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {'error': 'Could not connect to the server'},
                status=500
            )
    
    return render(request, 'contac.html')

@login_required
def help_center(request):
    return render(request, 'helpandcenter.html')

@login_required
def random_quiz(request):
    """View function for the random quiz generator page."""
    return render(request, 'ss.html')

# New Flask API Integration Code
def login_user(email, password):
    """Login a user through the Flask API"""
    try:
        # Validate required fields
        if not email or not password:
            return False, "Email and password are required"
            
        print("\n=== Login Request Details ===")
        print(f"URL: {LOGIN_URL}")
        print(f"Email: {email}")
        
        # Add headers to ensure proper content type
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare the request data
        data = {
            'email': email,
            'password': password
        }
        
        print(f"Request Headers: {headers}")
        print(f"Request Data: {data}")
        
        response = requests.post(
            LOGIN_URL,
            json=data,
            headers=headers
        )
        
        print("\n=== Login Response Details ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content.decode()}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                # The Flask API returns the token in the response
                if 'access_token' in data:
                    return True, data['access_token']
                return render(request, 'home.html')
                return False, "No access token received from server"
            except Exception as e:
                print(f"Error parsing response JSON: {str(e)}")
                return False, "Invalid response format"
        elif response.status_code == 401:
            try:
                error_data = response.json()
                return False, error_data.get('message', 'Invalid email or password')
            except:
                return False, "Invalid email or password"
        else:
            try:
                error_data = response.json()
                return False, error_data.get('message', 'Login failed')
            except:
                return False, f"Login failed: {response.text}"
                
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {str(e)}")
        return False, f"Login failed: {str(e)}"
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        return False, f"Login failed: {str(e)}"
    

def register_user(name, email, mobile, password):
    """Register a new user through the Flask API"""
    try:
        # Validate required fields
        if not all([name, email, mobile, password]):
            missing_fields = []
            if not name: missing_fields.append('name')
            if not email: missing_fields.append('email')
            if not mobile: missing_fields.append('mobile')
            if not password: missing_fields.append('password')
            return False, f"Missing required fields: {', '.join(missing_fields)}"
            
        print("\n=== Registration Request Details ===")
        print(f"URL: {REGISTER_URL}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Mobile: {mobile}")
        print(f"Password length: {len(password)}")
        
        # Add headers to ensure proper content type
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare the request data
        data = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'password': password
        }
        
        print(f"Request Headers: {headers}")
        print(f"Request Data: {data}")
        
        response = requests.post(
            REGISTER_URL,
            json=data,
            headers=headers
        )
        
        print("\n=== Registration Response Details ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content.decode()}")
        
        if response.status_code == 201:
            return True, "Registration successful"
        else:
            try:
                error_data = response.json()
                return False, error_data.get('message', 'Registration failed')
            except:
                return False, f"Registration failed: {response.text}"
                
    except requests.exceptions.RequestException as e:
        print(f"Registration request failed: {str(e)}")
        return False, f"Registration failed: {str(e)}"
    except Exception as e:
        print(f"Unexpected error during registration: {str(e)}")
        return False, f"Registration failed: {str(e)}"

def get_user_profile(jwt_token):
    """
    Get user profile from Flask API using JWT token
    """
    try:
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(PROFILE_URL, headers=headers)
        print(f"Profile Response: {response.status_code} - {response.text}")  # Debug print
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting profile: {str(e)}")
        return None

# New View Functions
def register_view(request):
    if request.method == 'POST':
        # Get form data and print for debugging
        print("\n=== Raw Registration POST Data ===")
        print(f"POST data: {request.POST}")
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        
        print("\n=== Registration Form Data ===")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Mobile: {mobile}")
        print(f"Password length: {len(password) if password else 0}")
        
        # Validate required fields
        if not all([name, email, mobile, password]):
            missing_fields = []
            if not name: missing_fields.append('name')
            if not email: missing_fields.append('email')
            if not mobile: missing_fields.append('mobile')
            if not password: missing_fields.append('password')
            messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
            return redirect('quiz:register')
            
        success, message = register_user(name, email, mobile, password)
        
        if success:
            # Clear any existing messages
            storage = messages.get_messages(request)
            storage.used = True
            
            # Add success message
            messages.success(request, "Registration successful! Please login.")
            
            # Redirect to login page
            return HttpResponseRedirect(reverse('quiz:login'))
        else:
            messages.error(request, message)
            return redirect('quiz:register')
            
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        # Get form data and print for debugging
        print("\n=== Raw POST Data ===")
        print(f"POST data: {request.POST}")
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print("\n=== Login Form Data ===")
        print(f"Email from form: {email}")
        print(f"Password length from form: {len(password) if password else 0}")
        
        # Validate required fields
        if not email:
            messages.error(request, "Email is required")
            return redirect('quiz:login')
        if not password:
            messages.error(request, "Password is required")
            return redirect('quiz:login')
            
        success, token = login_user(email, password)
        
        if success:
            # Store the JWT token in the session
            request.session['jwt_token'] = token
            
            # Create or get CustomUser
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                # Create a new user if they don't exist
                # Use email as username if no username is provided
                username = email.split('@')[0]  # Use part before @ as username
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
            
            # Log the user in with the default authentication backend
            from django.contrib.auth import get_backends
            backend = get_backends()[0]  # Get the first authentication backend
            login(request, user, backend=backend.__class__.__module__ + '.' + backend.__class__.__name__)
            
            messages.success(request, "Login successful")
            return redirect('quiz:home')
        else:
            messages.error(request, token)  # token contains error message in this case
            return redirect('quiz:login')
            
    return render(request, 'login.html')

def profile_view(request):
    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.error(request, "Please login first")
        return redirect('quiz:login')
    
    # Get user profile data
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    
    # Get user's challenges
    received_challenges = Challenge.objects.filter(receiver=request.user).order_by('-created_at')
    sent_challenges = Challenge.objects.filter(sender=request.user).order_by('-created_at')
    
    # Get user's achievements
    achievements = user_profile.achievements.all()
    
    # Get user's quiz statistics
    quiz_stats = {
        'total_points': user_profile.total_points,
        'quizzes_taken': user_profile.quizzes_taken,
        'quizzes_created': user_profile.quizzes_created,
    }
    
    # Handle profile form submission
    if request.method == 'POST':
        if 'profile_form' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('quiz:profile')
        elif 'challenge_form' in request.POST:
            challenge_form = ChallengeForm(request.POST)
            if challenge_form.is_valid():
                challenge = challenge_form.save(commit=False)
                challenge.sender = request.user
                challenge.save()
                messages.success(request, "Challenge sent successfully!")
                return redirect('quiz:profile')
    else:
        form = UserProfileForm(instance=user_profile)
        challenge_form = ChallengeForm()
    
    context = {
        'user': request.user,
        'profile': user_profile,
        'form': form,
        'challenge_form': challenge_form,
        'received_challenges': received_challenges,
        'sent_challenges': sent_challenges,
        'achievements': achievements,
        'quiz_stats': quiz_stats,
    }
    
    return render(request, 'profile.html', context)

def logout_view(request):
    # Clear session data
    if 'jwt_token' in request.session:
        del request.session['jwt_token']
    messages.success(request, "Logged out successfully!")
    return redirect('quiz:login')

@login_required
def dashboard(request):
    user_profile = request.user.profile
    
    # Get regular quiz attempts
    recent_attempts = QuizAttempt.objects.filter(
        user=request.user,
        completed=True
    ).order_by('-completed_at')[:5]
    
    # Get AI quiz attempts
    ai_quiz_attempts = None
    ai_stats = {
        'total_attempts': 0,
        'total_score': 0,
        'avg_percentage': 0,
        'highest_score': 0,
        'latest_attempt': None,
        'genres': {}  # Track genres for analytics
    }
    
    try:
        ai_quiz_attempts = AIQuizAttempt.objects.filter(
            user=request.user,
            completed=True
        ).order_by('-completed_at')
        
        if ai_quiz_attempts.exists():
            # Get the 5 most recent attempts for display
            recent_ai_attempts = ai_quiz_attempts[:5]
            
            # Calculate stats
            ai_stats['total_attempts'] = ai_quiz_attempts.count()
            ai_stats['total_score'] = sum(attempt.score for attempt in ai_quiz_attempts)
            ai_stats['avg_percentage'] = sum(attempt.percentage for attempt in ai_quiz_attempts) / ai_stats['total_attempts'] if ai_stats['total_attempts'] > 0 else 0
            ai_stats['highest_score'] = max(attempt.percentage for attempt in ai_quiz_attempts) if ai_stats['total_attempts'] > 0 else 0
            ai_stats['latest_attempt'] = ai_quiz_attempts.first()
            
            # Track genres/topics using title parsing
            for attempt in ai_quiz_attempts:
                # Extract topic from title (assumes format like "Science Quiz", "History Quiz", etc.)
                topic = attempt.quiz_title.split(' ')[0] if ' ' in attempt.quiz_title else 'General'
                
                if topic in ai_stats['genres']:
                    ai_stats['genres'][topic]['count'] += 1
                    ai_stats['genres'][topic]['score'] += attempt.score
                else:
                    ai_stats['genres'][topic] = {
                        'count': 1,
                        'score': attempt.score
                    }
            
            # Format genre stats
            for topic in ai_stats['genres']:
                count = ai_stats['genres'][topic]['count']
                total_score = ai_stats['genres'][topic]['score']
                ai_stats['genres'][topic]['avg_score'] = total_score / count
                
            # Update recent attempts to only show the 5 most recent
            ai_quiz_attempts = recent_ai_attempts
            
            # Try to get AIQuiz data for additional details
            try:
                from QuizAiApp.models import AIQuiz
                for attempt in ai_quiz_attempts:
                    if attempt.quiz_id and attempt.quiz_id.isdigit():
                        try:
                            quiz = AIQuiz.objects.get(id=int(attempt.quiz_id))
                            attempt.creation_date = quiz.created_at
                        except AIQuiz.DoesNotExist:
                            pass
            except (ImportError, Exception) as e:
                import logging
                logging.error(f"Error getting AIQuiz details: {e}")
                
    except (ImportError, Exception) as e:
        import logging
        logging.error(f"Error getting AI quiz attempts: {e}")
    
    created_quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    stats = {
        'total_points': user_profile.total_points,
        'quizzes_taken': user_profile.quizzes_taken,
        'quizzes_created': user_profile.quizzes_created,
        'achievements': user_profile.achievements.all(),
        'ai_stats': ai_stats
    }
    
    context = {
        'recent_attempts': recent_attempts,
        'ai_quiz_attempts': ai_quiz_attempts,
        'created_quizzes': created_quizzes,
        'stats': stats,
    }
    return render(request, 'dashboard.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Save the new password
            form.save()
            # Log out the user
            logout(request)
            # Add success message
            messages.success(request, 'Your password has been changed successfully. Please login with your new password.')
            # Redirect to login page
            return redirect('quiz:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'Q&N.html', {'quizzes': quizzes})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz.is_public and quiz.created_by != request.user:
        messages.error(request, 'This quiz is private.')
        return redirect('quiz:quiz_list')
    return render(request, 'a.html', {'quiz': quiz})

@login_required
def leaderboard(request):
    # Get all users ordered by total points for global ranking
    top_users = UserProfile.objects.order_by('-total_points')[:20]
    
    # Get users ordered by quizzes taken for most active users
    most_active_users = UserProfile.objects.order_by('-quizzes_taken')[:20]
    
    # Get users ordered by quizzes created for top creators
    top_creators = UserProfile.objects.order_by('-quizzes_created')[:20]
    
    # For top creators, get their most popular quiz and total attempts
    for creator in top_creators:
        created_quizzes = Quiz.objects.filter(created_by=creator.user)
        
        # Find the most popular quiz for this creator
        most_popular = None
        total_attempts = 0
        
        if created_quizzes.exists():
            for quiz in created_quizzes:
                attempts = QuizAttempt.objects.filter(quiz=quiz).count()
                total_attempts += attempts
                
                if most_popular is None or attempts > most_popular[1]:
                    most_popular = (quiz, attempts)
            
            if most_popular:
                creator.most_popular_quiz = most_popular[0].title
                creator.total_attempts = total_attempts
    
    # Get last quiz date for most active users
    for user in most_active_users:
        latest_attempt = QuizAttempt.objects.filter(
            user=user.user, 
            completed=True
        ).order_by('-completed_at').first()
        
        if latest_attempt:
            user.last_quiz_date = latest_attempt.completed_at
    
    # Get top challenge performers
    # First, get all challenge attempts
    challenge_attempts = QuizAttempt.objects.filter(
        is_challenge=True,
        completed=True
    ).order_by('-score', 'completed_at')
    
    # Get unique users with their best challenge score
    top_challengers = {}
    for attempt in challenge_attempts:
        user_id = attempt.user.id
        if user_id not in top_challengers or attempt.score > top_challengers[user_id]['score']:
            top_challengers[user_id] = {
                'user': attempt.user,
                'score': attempt.score,
                'quiz': attempt.quiz,
                'completed_at': attempt.completed_at
            }
    
    # Convert to list and sort by score (descending)
    top_challengers = sorted(
        top_challengers.values(), 
        key=lambda x: x['score'], 
        reverse=True
    )[:20]
    
    # Calculate maximum points for progress bars
    max_points = top_users[0].total_points if top_users.exists() else 100
    
    # Add custom template filter for percentage calculation
    from django import template
    register = template.Library()
    
    @register.filter
    def percentage(value, max_value):
        try:
            return min(value * 100 / max_value, 100)
        except (ValueError, ZeroDivisionError):
            return 0
    
    # Add custom filter for division
    @register.filter
    def divide(value, arg):
        try:
            return value / arg
        except (ValueError, ZeroDivisionError):
            return 0
            
    # Save the filters to a file if they don't exist yet
    import os
    templatetags_dir = os.path.join(os.path.dirname(__file__), 'templatetags')
    if not os.path.exists(templatetags_dir):
        os.makedirs(templatetags_dir)
        
    quiz_extras_path = os.path.join(templatetags_dir, 'quiz_extras.py')
    if not os.path.exists(quiz_extras_path):
        with open(quiz_extras_path, 'w') as f:
            f.write('''from django import template

register = template.Library()

@register.filter
def percentage(value, max_value):
    try:
        return min(value * 100 / max_value, 100)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    try:
        return value / arg
    except (ValueError, ZeroDivisionError):
        return 0
''')
        
        # Create __init__.py file in templatetags directory
        with open(os.path.join(templatetags_dir, '__init__.py'), 'w') as f:
            f.write('')
    
    # Get or create user profile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'top_users': top_users,
        'most_active_users': most_active_users,
        'top_creators': top_creators,
        'max_points': max_points,
        'profile': user_profile,
        'top_challengers': top_challengers,  # Add top challengers to context
    }
    return render(request, 'leaderboard.html', context)

@login_required
def created_quizzes(request):
    """View for displaying quizzes created by the user."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Find all AIQuizAttempts for this user
    ai_attempts = AIQuizAttempt.objects.filter(
        user=request.user,
        completed=True
    )
    logger.info(f"Found {ai_attempts.count()} total AI quiz attempts for user {request.user.username}")
    
    # Find quizzes created by this user
    created_quizzes = Quiz.objects.filter(created_by=request.user)
    logger.info(f"Found {created_quizzes.count()} quizzes created by user {request.user.username}")
    
    # Force create a quiz from existing attempts if requested
    if 'repair' in request.GET and 'create' in request.GET and ai_attempts.exists() and not created_quizzes.exists():
        # Get the most recent attempt to use its title
        latest_attempt = ai_attempts.order_by('-completed_at').first()
        quiz_title = latest_attempt.quiz_title or "AI Generated Quiz"
        
        # Create a new quiz
        new_quiz = Quiz.objects.create(
            title=quiz_title,
            description=f"Automatically created quiz for existing attempts",
            category="AI Quiz",
            created_by=request.user,
            created_at=timezone.now()
        )
        logger.info(f"Created new quiz: {new_quiz.title} (ID: {new_quiz.id})")
        
        # Associate all attempts with the new quiz
        for attempt in ai_attempts:
            attempt.quiz_id = str(new_quiz.id)
            attempt.save()
        
        messages.success(request, f"Created new quiz '{quiz_title}' and associated {ai_attempts.count()} attempts with it")
        
        # Refresh quizzes list
        created_quizzes = Quiz.objects.filter(created_by=request.user)
    
    # Run repair operation if requested
    elif 'debug' in request.GET or 'repair' in request.GET:
        logger.info("Running repair operation for quiz attempts")
        
        total_repairs = 0
        
        # First check for direct title matches
        for quiz in created_quizzes:
            quiz_id_str = str(quiz.id)
            quiz_title = quiz.title
            
            # Try to find attempts with matching title but no correct quiz_id
            title_matches = ai_attempts.filter(quiz_title__icontains=quiz_title)
            if title_matches.exists():
                logger.info(f"Found {title_matches.count()} attempts with title containing '{quiz_title}'")
                
                # Auto-associate attempts with this quiz
                repair_count = 0
                for attempt in title_matches:
                    if not attempt.quiz_id or attempt.quiz_id == 'None' or str(attempt.quiz_id) != quiz_id_str:
                        old_id = attempt.quiz_id
                        attempt.quiz_id = quiz_id_str
                        attempt.save()
                        repair_count += 1
                        logger.info(f"Updated attempt {attempt.id}: changed quiz_id from '{old_id}' to '{quiz_id_str}'")
                
                if repair_count > 0:
                    total_repairs += repair_count
                    messages.success(request, f"Fixed {repair_count} quiz attempts for '{quiz_title}'")
        
        # If no direct title matches but we have quizzes, use the first quiz
        if total_repairs == 0 and created_quizzes.exists() and ai_attempts.exists():
            logger.info("No direct matches found, trying more aggressive matching")
            
            # Get all attempts without a valid quiz_id or with a quiz_id that doesn't match any existing quiz
            unassigned_attempts = []
            for attempt in ai_attempts:
                try:
                    quiz_exists = Quiz.objects.filter(id=attempt.quiz_id).exists()
                    if not attempt.quiz_id or attempt.quiz_id == 'None' or not quiz_exists:
                        unassigned_attempts.append(attempt)
                except:
                    unassigned_attempts.append(attempt)
            
            if unassigned_attempts:
                logger.info(f"Found {len(unassigned_attempts)} unassigned attempts")
                
                # Match each attempt to the first quiz
                first_quiz = created_quizzes.first()
                quiz_id_str = str(first_quiz.id)
                
                for attempt in unassigned_attempts:
                    attempt.quiz_id = quiz_id_str
                    attempt.save()
                    total_repairs += 1
                
                messages.success(request, f"Associated {len(unassigned_attempts)} unassigned attempts with quiz '{first_quiz.title}'")
        
        # If still no repairs and we have quizzes but no repairs, create a new quiz
        if total_repairs == 0 and ai_attempts.exists() and not created_quizzes.exists():
            logger.info("Creating a new quiz to associate with existing attempts")
            
            # Get the most recent attempt to use its title
            latest_attempt = ai_attempts.order_by('-completed_at').first()
            quiz_title = latest_attempt.quiz_title or "AI Generated Quiz"
            
            # Create a new quiz
            new_quiz = Quiz.objects.create(
                title=quiz_title,
                description=f"Automatically created quiz for existing attempts",
                category="AI Quiz",
                created_by=request.user,
                created_at=timezone.now()
            )
            logger.info(f"Created new quiz: {new_quiz.title} (ID: {new_quiz.id})")
            
            # Associate all attempts with the new quiz
            for attempt in ai_attempts:
                attempt.quiz_id = str(new_quiz.id)
                attempt.save()
                total_repairs += 1
            
            messages.success(request, f"Created new quiz '{quiz_title}' and associated {total_repairs} attempts with it")
            
            # Refresh quizzes list
            created_quizzes = Quiz.objects.filter(created_by=request.user)
        
        if total_repairs == 0:
            if ai_attempts.count() == 0:
                messages.warning(request, "No quiz attempts found. Try taking a quiz first!")
            else:
                messages.warning(request, "No quiz attempts needed repair.")
        else:
            messages.success(request, f"Successfully repaired {total_repairs} quiz attempts in total")
    
    profile = request.user.profile
    
    # Check for unlinked attempts
    unlinked_attempts_count = 0
    if ai_attempts.exists():
        for attempt in ai_attempts:
            try:
                quiz_exists = False
                if attempt.quiz_id:
                    quiz_exists = created_quizzes.filter(id=attempt.quiz_id).exists()
                if not quiz_exists:
                    unlinked_attempts_count += 1
            except:
                unlinked_attempts_count += 1
    
    # Get attempts for each quiz
    for quiz in created_quizzes:
        quiz.attempts = quiz.get_attempts()
    
    # Define the get_ai_quiz_attempts function for the template
    def get_ai_quiz_attempts(quiz_id=None):
        """Get AI quiz attempts for the specified quiz ID"""
        return AIQuizAttempt.objects.filter(
            quiz_id=str(quiz_id),
            completed=True
        ).order_by('-completed_at')
    
    # Create a class to pass to the template with the helper method
    class ViewHelper:
        @staticmethod
        def get_ai_quiz_attempts(quiz_id=None):
            """Helper method for the template that accepts a named parameter"""
            return get_ai_quiz_attempts(quiz_id)
    
    return render(request, 'created_quizzes.html', {
        'created_quizzes': created_quizzes,
        'profile': profile,
        'view': ViewHelper,
        'ai_attempts_count': unlinked_attempts_count
    })

@login_required
def my_quizzes(request):
    """View for displaying both quizzes created by the user and quizzes taken by the user."""
    # Get user profile
    profile = request.user.profile
    
    # Get quizzes created by the user
    created_quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Get user's quiz attempts (regular quizzes)
    quiz_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-completed_at')
    
    # Get user's AI quiz attempts
    ai_quiz_attempts = AIQuizAttempt.objects.filter(user=request.user, completed=True).order_by('-completed_at')
    
    # Get all quizzes the user has attempted
    attempted_quiz_ids = quiz_attempts.values_list('quiz_id', flat=True).distinct()
    attempted_quizzes = Quiz.objects.filter(id__in=attempted_quiz_ids)
    
    # Count total attempts
    total_attempts = quiz_attempts.count() + ai_quiz_attempts.count()
    
    return render(request, 'my_quizzes.html', {
        'created_quizzes': created_quizzes,
        'quiz_attempts': quiz_attempts,
        'ai_quiz_attempts': ai_quiz_attempts,
        'attempted_quizzes': attempted_quizzes,
        'profile': profile,
        'total_attempts': total_attempts
    })

@login_required
def create_quiz(request):
    if request.method == 'POST':
        # Process form submission to create a new quiz
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        difficulty = request.POST.get('difficulty')
        is_public = request.POST.get('is_public') == 'on'
        
        # Create the quiz
        quiz = Quiz.objects.create(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            is_public=is_public,
            created_by=request.user,
            created_at=timezone.now()
        )
        
        # Update user profile stats
        profile = request.user.profile
        profile.quizzes_created += 1
        profile.save()
        
        # Process questions
        for i in range(1, int(request.POST.get('question_count', 0)) + 1):
            question_text = request.POST.get(f'question_{i}')
            if question_text:
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=question_text,
                    order=i
                )
                
                # Process options for this question
                for j in range(1, 5):  # Assuming 4 options per question
                    option_text = request.POST.get(f'question_{i}_option_{j}')
                    is_correct = request.POST.get(f'question_{i}_correct') == str(j)
                    
                    if option_text:
                        Choice.objects.create(
                            question=question,
                            choice_text=option_text,
                            is_correct=is_correct
                        )
        
        messages.success(request, 'Quiz created successfully!')
        return redirect('quiz:created_quizzes')
    
    return render(request, 'create_quiz.html', {'profile': request.user.profile})

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the creator of the quiz
    if quiz.created_by != request.user:
        messages.error(request, "You don't have permission to edit this quiz.")
        return redirect('quiz:dashboard')
    
    if request.method == 'POST':
        # Update quiz details
        quiz.title = request.POST.get('title')
        quiz.description = request.POST.get('description')
        quiz.category = request.POST.get('category')
        quiz.difficulty = request.POST.get('difficulty')
        quiz.is_public = request.POST.get('is_public') == 'on'
        quiz.save()
        
        messages.success(request, 'Quiz updated successfully!')
        return redirect('quiz:view_quiz', quiz_id=quiz.id)
    
    context = {
        'quiz': quiz,
        'profile': request.user.profile,
    }
    return render(request, 'edit_quiz.html', context)

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the creator of the quiz
    if quiz.created_by != request.user:
        messages.error(request, "You don't have permission to delete this quiz.")
        return redirect('quiz:dashboard')
    
    if request.method == 'POST':
        # Delete the quiz
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('quiz:created_quizzes')
    
    # GET request renders confirmation page
    context = {
        'quiz': quiz,
        'profile': request.user.profile,
    }
    return render(request, 'delete_quiz_confirm.html', context)

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the creator of the quiz
    if quiz.created_by != request.user:
        messages.error(request, "You don't have permission to edit this quiz.")
        return redirect('quiz:dashboard')
    
    if request.method == 'POST':
        # Get question data from POST request
        question_text = request.POST.get('question_text')
        points = request.POST.get('points', 1)
        
        # Create question
        question = Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            points=points,
            order=quiz.questions.count() + 1  # Set order to next available position
        )
        
        # Create choices
        for i in range(1, 5):  # Assuming 4 choices
            choice_text = request.POST.get(f'choice_{i}')
            is_correct = request.POST.get(f'is_correct') == str(i)
            
            if choice_text:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct
                )
        
        messages.success(request, 'Question added successfully!')
        return redirect('quiz:edit_quiz', quiz_id=quiz.id)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    
    # Check if user is the creator of the quiz
    if quiz.created_by != request.user:
        messages.error(request, "You don't have permission to edit this question.")
        return redirect('quiz:dashboard')
    
    if request.method == 'POST':
        # Update question
        question.question_text = request.POST.get('question_text')
        question.points = request.POST.get('points', 1)
        question.save()
        
        # Update choices
        # First, get all existing choices
        existing_choices = {choice.id: choice for choice in question.choices.all()}
        
        for i in range(1, 5):  # Assuming 4 choices
            choice_text = request.POST.get(f'choice_{i}')
            choice_id = request.POST.get(f'choice_id_{i}')
            is_correct = request.POST.get('is_correct') == str(i)
            
            if choice_id and choice_id.isdigit() and int(choice_id) in existing_choices:
                # Update existing choice
                choice = existing_choices[int(choice_id)]
                choice.choice_text = choice_text
                choice.is_correct = is_correct
                choice.save()
                # Remove from dict to track which ones were updated
                del existing_choices[int(choice_id)]
            elif choice_text:
                # Create new choice
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct
                )
        
        # Delete any choices not updated
        for choice in existing_choices.values():
            choice.delete()
        
        messages.success(request, 'Question updated successfully!')
        return redirect('quiz:edit_quiz', quiz_id=quiz.id)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    
    # Check if user is the creator of the quiz
    if quiz.created_by != request.user:
        messages.error(request, "You don't have permission to delete this question.")
        return JsonResponse({'status': 'error', 'message': 'Permission denied'})
    
    if request.method == 'POST':
        # Delete the question
        question.delete()
        
        # Reorder remaining questions
        for i, q in enumerate(quiz.questions.all().order_by('order')):
            q.order = i + 1
            q.save()
        
        return JsonResponse({'status': 'success', 'message': 'Question deleted successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def get_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    
    # Check if user is the creator of the quiz
    if quiz.created_by != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    # Get choices
    choices = []
    for choice in question.choices.all():
        choices.append({
            'id': choice.id,
            'choice_text': choice.choice_text,
            'is_correct': choice.is_correct
        })
    
    # Return question data as JSON
    return JsonResponse({
        'question_text': question.question_text,
        'points': question.points,
        'choices': choices
    })

@login_required
def view_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if the quiz is public or the user is the creator
    if not quiz.is_public and quiz.created_by != request.user:
        messages.error(request, "You don't have permission to view this quiz.")
        return redirect('quiz:dashboard')
    
    # Get all questions for this quiz with their choices
    questions = Question.objects.filter(quiz=quiz).order_by('order')
    
    # Get attempt history for this quiz by current user
    attempts = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz,
        completed=True
    ).order_by('-completed_at')
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'attempts': attempts,
        'profile': request.user.profile,
        'is_creator': quiz.created_by == request.user,
    }
    return render(request, 'view_quiz.html', context)

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz.is_public and quiz.created_by != request.user:
        messages.error(request, 'This quiz is private.')
        return redirect('quiz:quiz_list')
    
    attempt, created = QuizAttempt.objects.get_or_create(
        user=request.user,
        quiz=quiz,
        defaults={'started_at': timezone.now()}
    )
    
    if not created and attempt.completed:
        messages.info(request, 'You have already completed this quiz!')
        return redirect('quiz:quiz_list')
    
    return render(request, 'a.html', {'quiz': quiz, 'attempt': attempt})

@login_required
def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        attempt = get_object_or_404(QuizAttempt, user=request.user, quiz=quiz)
        
        if not attempt.completed:
            score = 0
            max_score = quiz.questions.aggregate(total=Sum('points'))['total'] or 0
            
            # Clear previous selections
            attempt.selected_choices.clear()
            
            for question in quiz.questions.all():
                answer_id = request.POST.get(f'question_{question.id}')
                if answer_id:
                    selected_choice = get_object_or_404(Choice, id=answer_id)
                    attempt.selected_choices.add(selected_choice)
                    if selected_choice.is_correct:
                        score += question.points
            
            attempt.score = score
            attempt.completed = True
            attempt.completed_at = timezone.now()
            attempt.passed = (score / max_score * 100) >= quiz.passing_score
            attempt.save()
            
            # Update user profile stats
            request.user.profile.update_stats()
            
            # Check for achievements
            check_achievements(request.user)
            
            # If this is a challenge attempt, update the challenge status
            if attempt.is_challenge and attempt.challenge:
                attempt.challenge.status = 'completed'
                attempt.challenge.save()
                percentage = (score / max_score) * 100 if max_score > 0 else 0
                messages.success(
                    request, 
                    f'Challenge completed! Your score: {score}/{max_score} ({percentage:.1f}%). '
                    f'This score has been added to the Challenges leaderboard.'
                )
                # Redirect to the leaderboard with challenges tab active
                return redirect(reverse('quiz:leaderboard') + '?tab=challenges')
            
            messages.success(request, f'Quiz completed! Your score: {score}/{max_score}')
        return redirect('quiz:leaderboard')
    return redirect('quiz:quiz_list')

def check_achievements(user):
    profile = user.profile
    achievements = Achievement.objects.all()
    
    for achievement in achievements:
        if (profile.total_points >= achievement.points_required and
            profile.quizzes_taken >= achievement.quizzes_required and
            achievement not in profile.achievements.all()):
            profile.achievements.add(achievement)
            messages.info(user, f'New Achievement Unlocked: {achievement.name}!')

@login_required
def accept_challenge(request, challenge_id):
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id, receiver=request.user)
        if challenge.status == 'pending':
            challenge.status = 'accepted'
            challenge.save()
            messages.success(request, f'You accepted the challenge for quiz: {challenge.quiz.title}')
        else:
            messages.warning(request, f'This challenge is already {challenge.status}.')
    except Exception as e:
        messages.error(request, f'Error accepting challenge: {str(e)}')
    return redirect('quiz:profile')

@login_required
def decline_challenge(request, challenge_id):
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id, receiver=request.user)
        if challenge.status == 'pending':
            challenge.status = 'declined'
            challenge.save()
            messages.success(request, 'Challenge declined.')
        else:
            messages.warning(request, f'This challenge is already {challenge.status}.')
    except Exception as e:
        messages.error(request, f'Error declining challenge: {str(e)}')
    return redirect('quiz:profile')

@login_required
def take_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id, receiver=request.user)
    if challenge.status in ['pending', 'accepted']:
        # Update challenge status if it's pending
        if challenge.status == 'pending':
            challenge.status = 'accepted'
            challenge.save()
            
        # Get the quiz
        quiz = challenge.quiz
        
        # Check if user already has an attempt for this quiz
        try:
            # Try to get an existing attempt
            attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz)
            
            # If attempt exists and is not completed, update it to mark as challenge
            if not attempt.completed:
                attempt.is_challenge = True
                attempt.challenge = challenge
                attempt.save()
            elif attempt.completed:
                # If attempt is completed, inform user
                messages.info(request, 'You have already completed this quiz!')
                return redirect('quiz:profile')
                
        except QuizAttempt.DoesNotExist:
            # Create new attempt if none exists
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                is_challenge=True,
                challenge=challenge,
                started_at=timezone.now()
            )
            
        # Start the quiz
        return render(request, 'a.html', {'quiz': quiz, 'attempt': attempt, 'is_challenge': True})
    else:
        messages.error(request, 'This challenge cannot be taken.')
        return redirect('quiz:profile')

def dashboard_view(request):
    # Check if user is logged in
    if 'jwt_token' not in request.session:
        messages.error(request, "Please login first")
        return redirect('quiz:login')
        
    return render(request, 'dashboard.html')