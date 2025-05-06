# Quiz Application Workspace

This workspace contains two separate quiz application projects:

## 1. Flask Quiz api

A comprehensive quiz platform built with Flask that allows users to take quizzes across different categories, create custom quizzes, and track their progress on leaderboards.

### Features
- User authentication (register, login, profile management)
- Multiple quiz categories (music, language, puzzle, math)
- Custom quiz creation and sharing
- Leaderboards to track top performers
- API endpoints for integration with other services
- Contact form and team information

### Tech Stack
- **Backend**: Flask, SQLAlchemy, JWT authentication
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Jinja2 templates

### Installation
```bash
cd 123
pip install -r requirements.txt
flask run
```

## 2. Django Quiz Application (DJANGO_QUIZ/)

A Django-based quiz platform that integrates with the Flask application's API for sharing quiz data.

### Features
- Django admin interface
- Integration with Flask quiz API
- Modern UI with multiple themes

### Tech Stack
- **Backend**: Django
- **API Client**: Requests library for Flask API integration
- **Frontend**: Django templates, CSS

### Installation
```bash
cd DJANGO_QUIZ
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Project Structure
- `123/` - Flask Quiz Application
  - `app.py` - Main application file
  - `models/` - Database models
  - `resources/` - API resources
  - `templates/` - HTML templates
  - `static/` - CSS, JS, and image files
  - `requirements.txt` - Dependencies

- `DJANGO_QUIZ/` - Django Quiz Application
  - `QuizProject/` - Django project files
  - `api_client.py` - Client for Flask API integration
  - `requirements.txt` - Dependencies

## Usage
1. Start the Flask application first (serves as the backend API)
2. Start the Django application (provides alternative frontend)
3. Create an account and start exploring quizzes!

## License
This project is proprietary software.

## Contact
For questions or issues, please use the contact form in the application.