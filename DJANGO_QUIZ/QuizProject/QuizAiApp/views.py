from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
import json
import time
import secrets
import requests
from datetime import datetime
from openai import OpenAI
import logging
from .models import AIQuiz, TobbiAPIConfig
from fpdf import FPDF
import uuid
from django.contrib import messages
from django.utils import timezone
from QuizTemplateApp.models import AIQuizAttempt, Quiz
from .sample_quiz_data import get_sample_quiz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("quiz_app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Replace with your actual API key
OPENROUTER_API_KEY = "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"
SITE_URL = "https://your-quiz-site.com"
SITE_NAME = "AI Quiz Generator"

def get_active_tobbi_config():
    """
    Retrieve the active TOBBI API configuration from the database.
    Falls back to environment settings if no active configuration exists.
    """
    try:
        config = TobbiAPIConfig.objects.filter(is_active=True).first()
        if config:
            return {
                'api_key': config.api_key,
                'base_url': config.base_url,
                'model': config.model
            }
    except Exception as e:
        logger.error(f"Error retrieving TOBBI API config: {str(e)}")
    
    # Fallback to default values
    return {
        'api_key': settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else OPENROUTER_API_KEY,
        'base_url': "https://openrouter.ai/api/v1",
        'model': "deepseek/deepseek-r1:free"
    }

class QuizGenerator:
    def __init__(self, api_key=None, base_url=None, model=None):
        # Get configuration from database or use provided values
        if not all([api_key, base_url, model]):
            config = get_active_tobbi_config()
            self.api_key = api_key or config['api_key']
            self.base_url = base_url or config['base_url']
            self.model = model or config['model']
        else:
            self.api_key = api_key
            self.base_url = base_url
            self.model = model
        
        self.last_error = None
            
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.last_error = f"Error initializing OpenAI client: {str(e)}"
            self.client = None
    
    def generate_quiz(self, topic, num_questions, difficulty="medium"):
        """Generate quiz questions using DeepSeek AI via OpenRouter."""
        try:
            system_prompt = (
                "You are an expert quiz creator. Create a multiple-choice quiz based on the user's request. "
                f"Generate exactly {num_questions} questions. "
                f"The difficulty level should be {difficulty}. "
                "For each question, provide 4 options (A, B, C, D) and mark the correct answer. "
                "Format your response as a JSON array with this structure for each question:\n"
                "{\n"
                "  \"question\": \"Question text\",\n"
                "  \"options\": [\"A. Option A\", \"B. Option B\", \"C. Option C\", \"D. Option D\"],\n"
                "  \"correct_answer\": \"A\",\n"
                "  \"explanation\": \"Brief explanation of the correct answer\"\n"
                "}\n"
                "IMPORTANT: Your response MUST be valid JSON only. Do not include any explanatory text before or after the JSON. "
                "Ensure all questions are factually accurate and educational."
            )
            
            user_prompt = f"Create a quiz with {num_questions} questions about: {topic}"
            
            logger.info(f"Generating quiz on topic: {topic}, questions: {num_questions}, difficulty: {difficulty}")
            logger.info(f"Using API key: {self.api_key[:5]}***, base URL: {self.base_url}, model: {self.model}")
            
            # Use OpenAI client
            try:
                response = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": SITE_URL,
                        "X-Title": SITE_NAME,
                        "X-Prompt-Training": "allow"
                    },
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Verify response contains choices
                if not hasattr(response, 'choices') or not response.choices:
                    # Check for error in response
                    if hasattr(response, 'error'):
                        error_msg = response.error.get('message', 'Unknown API error')
                        error_code = response.error.get('code', 'unknown')
                        logger.error(f"API error {error_code}: {error_msg}")
                        self.last_error = f"API error: {error_msg}"
                        
                        # Special handling for rate limits
                        if error_code == 429 or 'rate limit' in error_msg.lower():
                            self.last_error = f"Rate limit exceeded: {error_msg}"
                    else:
                        logger.error(f"API response does not contain choices: {response}")
                        self.last_error = "API response does not contain expected data format"
                    return None
                    
                # Check if choice contains a message
                choice = response.choices[0]
                if not hasattr(choice, 'message') or not choice.message:
                    logger.error(f"API response choice does not contain a message: {choice}")
                    self.last_error = "API response is missing message content"
                    return None
                    
                # Extract the content from the API response
                content = choice.message.content
                if not content:
                    logger.error("API response message content is empty")
                    self.last_error = "API returned empty response"
                    return None
                    
                logger.info("Successfully received content from API")
            except Exception as api_error:
                logger.error(f"API request failed: {str(api_error)}")
                self.last_error = f"API request failed: {str(api_error)}"
                return None
            
            # Parse the JSON content
            try:
                if isinstance(content, str):
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif content.startswith("```"):
                        content = content.split("```")[1].split("```")[0].strip()
                
                logger.info(f"Raw content from API: {content[:100]}...")  # Log first 100 chars
                quiz_data = json.loads(content)
                
                # Handle different possible formats
                if "questions" in quiz_data:
                    questions = quiz_data["questions"]
                elif isinstance(quiz_data, list):
                    questions = quiz_data
                else:
                    questions = [quiz_data]  # Single question case
                
                if not questions:
                    logger.error("No questions found in the API response")
                    return None
                    
                logger.info(f"Successfully parsed {len(questions)} questions from JSON")
                
                # Validate each question and ensure correct format
                formatted_questions = []
                for i, q in enumerate(questions):
                    # Ensure all required fields are present
                    if not all(key in q for key in ["question", "options", "correct_answer"]):
                        logger.warning(f"Question {i} is missing required fields: {q}")
                        continue
                    
                    # Ensure options are formatted correctly as a list of strings
                    if not isinstance(q["options"], list):
                        logger.warning(f"Options for question {i} are not in a list format: {q['options']}")
                        continue
                    
                    # Ensure we have 4 options
                    if len(q["options"]) != 4:
                        logger.warning(f"Question {i} does not have exactly 4 options: {q['options']}")
                        # Try to fix by adding generic options if needed
                        while len(q["options"]) < 4:
                            q["options"].append(f"{chr(65 + len(q['options']))}. Option {chr(65 + len(q['options']))}")
                        # Trim if too many
                        if len(q["options"]) > 4:
                            q["options"] = q["options"][:4]
                    
                    # Make sure options start with A, B, C, D
                    for j, option in enumerate(q["options"]):
                        prefix = f"{chr(65 + j)}. "
                        if not str(option).startswith(prefix):
                            q["options"][j] = f"{prefix}{option}"
                    
                    # Ensure correct_answer is valid (A, B, C, or D)
                    if q["correct_answer"] not in ["A", "B", "C", "D"]:
                        # Try to extract just the letter if possible
                        if q["correct_answer"].startswith("A"):
                            q["correct_answer"] = "A"
                        elif q["correct_answer"].startswith("B"):
                            q["correct_answer"] = "B"
                        elif q["correct_answer"].startswith("C"):
                            q["correct_answer"] = "C"
                        elif q["correct_answer"].startswith("D"):
                            q["correct_answer"] = "D"
                        else:
                            # Default to first option if we can't determine
                            q["correct_answer"] = "A"
                            logger.warning(f"Invalid correct_answer for question {i}: {q['correct_answer']}")
                    
                    formatted_questions.append(q)
                
                logger.info(f"Formatted {len(formatted_questions)} questions successfully")
                
                if not formatted_questions:
                    logger.error(f"No valid questions found in response")
                    return {"error": "No valid questions found in the response", "raw_content": content}
                
                return formatted_questions
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}\nContent: {content}")
                self.last_error = f"Could not parse API response as valid JSON: {str(e)}"
                return None
        
        except Exception as e:
            logger.error(f"Unexpected error in generate_quiz: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.last_error = f"Unexpected error: {str(e)}"
            return None

    def edit_quiz(self, current_questions, edit_prompt):
        """Edit existing quiz based on user feedback."""
        try:
            # Convert current questions to JSON string
            current_quiz_json = json.dumps(current_questions)
            
            system_prompt = (
                "You are an expert quiz editor. The user will provide you with an existing quiz and instructions "
                "on how to modify it. Edit the quiz according to their instructions while maintaining the format. "
                "Return the complete edited quiz in the same JSON format. "
                "IMPORTANT: Your response MUST be valid JSON only. Do not include any explanatory text before or after the JSON."
            )
            
            user_prompt = f"Here is my current quiz:\n{current_quiz_json}\n\nPlease make these changes: {edit_prompt}"
            
            # Use OpenAI client
            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": SITE_URL,
                    "X-Title": SITE_NAME,
                    "X-Prompt-Training": "allow"
                },
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract content from API response
            content = response.choices[0].message.content
            
            # Parse JSON content
            try:
                if isinstance(content, str):
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif content.startswith("```"):
                        content = content.split("```")[1].split("```")[0].strip()
                    
                    # Try to extract JSON from text
                    import re
                    json_pattern = r'\[\s*{.*}\s*\]|{\s*".*}'
                    json_matches = re.search(json_pattern, content, re.DOTALL)
                    if json_matches:
                        content = json_matches.group(0)
                
                quiz_data = json.loads(content)
                
                # Handle different possible formats
                if "questions" in quiz_data:
                    questions = quiz_data["questions"]
                elif isinstance(quiz_data, list):
                    questions = quiz_data
                else:
                    questions = [quiz_data]
                
                # Validate questions format
                valid_questions = []
                for q in questions:
                    if all(key in q for key in ["question", "options", "correct_answer"]):
                        valid_questions.append(q)
                
                if not valid_questions:
                    logger.error(f"No valid questions found in edit response: {content}")
                    return {"error": "No valid questions found in the edited response", "raw_content": content}
                
                return {"questions": valid_questions}
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}\nContent: {content}")
                return {"error": "Failed to parse edited quiz data. Please try again.", "raw_content": content}
        
        except Exception as e:
            logger.error(f"Edit quiz error: {e}")
            return {"error": f"Error editing quiz: {str(e)}"}

def generate_quiz_pdf(quiz_data, user_answers=None, score=None):
    """Generate a PDF of the quiz questions and answers."""
    try:
        # Ensure the directory exists
        pdf_dir = os.path.join(settings.MEDIA_ROOT, "quizai_downloads")
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Use a different approach - create a simple HTML file and convert it
        timestamp = int(time.time())
        random_str = secrets.token_hex(4)  # Add randomness to prevent filename collisions
        filename = f"quiz_{timestamp}_{random_str}.pdf"
        pdf_path = os.path.join(pdf_dir, filename)
        
        # If quiz_data is empty or None, create a dummy template
        if not quiz_data:
            # Create empty PDF with message
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "AI Generated Quiz", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
                pdf.ln(10)
                pdf.set_font("Arial", "I", 12)
                pdf.cell(0, 10, "No quiz data available for download.", ln=True)
                pdf.output(pdf_path)
                logger.info(f"Empty PDF generated as fallback: {pdf_path}")
                return filename
            except Exception as e:
                logger.error(f"Failed to generate empty PDF: {e}")
                return None
        
        # Create a simple HTML file
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>AI Generated Quiz</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2 {{ color: #4a6bff; }}
                .question {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
                .options {{ margin-left: 20px; }}
                .answer {{ font-weight: bold; color: #28a745; }}
                .explanation {{ font-style: italic; color: #555; }}
                .user-answer {{ margin-top: 10px; }}
                .correct {{ color: #28a745; }}
                .incorrect {{ color: #dc3545; }}
                .score-section {{ margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>AI Generated Quiz</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """
        
        # Add questions
        for i, q in enumerate(quiz_data):
            # Ensure question is properly formatted and displayed
            question_text = q.get('question', f'Question {i+1}')
            html_content += f"""
            <div class="question">
                <h3>Question {i+1}: {question_text}</h3>
                <div class="options">
            """
            
            # Add options - ensure options list exists and is properly displayed
            options = q.get("options", [])
            if options:
                for option in options:
                    html_content += f"<p>{option}</p>"
            else:
                html_content += "<p><em>No options available</em></p>"
            
            # Add correct answer and explanation
            correct_answer = q.get('correct_answer', 'Not provided')
            html_content += f"""
                </div>
                <p class="answer">Correct Answer: {correct_answer}</p>
            """
            
            if "explanation" in q and q["explanation"]:
                html_content += f'<p class="explanation">Explanation: {q.get("explanation")}</p>'
            
            # Add user's answer if available
            user_answer = user_answers[i] if user_answers and i < len(user_answers) else None
            if user_answer:
                is_correct = user_answer == correct_answer
                result_class = "correct" if is_correct else "incorrect"
                result_text = "Correct" if is_correct else "Incorrect"
                html_content += f"""
                <div class="user-answer">
                    <p>Your Answer: {user_answer} <span class="{result_class}">({result_text})</span></p>
                </div>
                """
            
            html_content += "</div>"
        
        # Add score if available
        if score is not None:
            percentage = (score / len(quiz_data)) * 100 if len(quiz_data) > 0 else 0
            html_content += f"""
            <div class="score-section">
                <h2>Final Score: {score}/{len(quiz_data)}</h2>
                <p>Percentage: {percentage:.1f}%</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # For HTML to PDF conversion, let's use pdfkit if available, otherwise fallback to simple file
        try:
            # First try to use pdfkit if installed
            import pdfkit
            pdfkit.from_string(html_content, pdf_path)
            logger.info(f"PDF generated with pdfkit: {pdf_path}")
        except (ImportError, Exception) as e:
            logger.warning(f"pdfkit conversion failed: {e}, falling back to FPDF")
            # If pdfkit is not available, we'll use a simpler approach with FPDF
            try:
                from fpdf import FPDF
                
                # Create PDF with FPDF
                pdf = FPDF()
                pdf.add_page()
                
                # PDF Setup
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "AI Generated Quiz", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
                pdf.ln(10)
                
                # Add questions - avoid special characters that cause encoding issues
                for i, q in enumerate(quiz_data):
                    # Replace special characters with safe alternatives
                    safe_question = q.get('question', f'Question {i+1}').replace('\u221a', 'sqrt').replace('²', '^2')
                    
                    pdf.set_font("Arial", "B", 12)
                    pdf.multi_cell(0, 10, f"Question {i+1}: {safe_question}")
                    pdf.ln(5)
                    
                    pdf.set_font("Arial", "", 12)
                    options = q.get("options", [])
                    if options:
                        for option in options:
                            # Replace special characters
                            safe_option = option.replace('\u221a', 'sqrt').replace('²', '^2')
                            pdf.multi_cell(0, 8, f"{safe_option}")
                    else:
                        pdf.multi_cell(0, 8, "No options available")
                    
                    pdf.ln(5)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, f"Correct Answer: {q.get('correct_answer', 'Not provided')}", ln=True)
                    
                    explanation = q.get('explanation', '')
                    if explanation:
                        # Replace special characters
                        safe_explanation = explanation.replace('\u221a', 'sqrt').replace('²', '^2')
                        pdf.set_font("Arial", "I", 12)
                        pdf.multi_cell(0, 10, f"Explanation: {safe_explanation}")
                    
                    # Add user's answer if available
                    user_answer = user_answers[i] if user_answers and i < len(user_answers) else None
                    if user_answer:
                        pdf.set_font("Arial", "", 12)
                        pdf.cell(0, 10, f"Your Answer: {user_answer}", ln=True)
                        is_correct = user_answer == q.get("correct_answer")
                        pdf.cell(0, 10, f"Result: {'Correct' if is_correct else 'Incorrect'}", ln=True)
                    
                    pdf.ln(10)
                
                # Add score if available
                if score is not None:
                    percentage = (score / len(quiz_data)) * 100 if len(quiz_data) > 0 else 0
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, f"Final Score: {score}/{len(quiz_data)}", ln=True)
                    pdf.cell(0, 10, f"Percentage: {percentage:.1f}%", ln=True)
                
                # Save PDF
                pdf.output(pdf_path)
                logger.info(f"PDF generated with FPDF (safe mode): {pdf_path}")
            except Exception as e:
                # If even the FPDF approach fails, we'll save the HTML content
                logger.error(f"PDF generation with FPDF failed: {e}")
                # Save as HTML instead
                html_path = os.path.join(pdf_dir, f"quiz_{timestamp}_{random_str}.html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Saved as HTML instead: {html_path}")
                # Return HTML filename instead
                return f"quiz_{timestamp}_{random_str}.html"
        
        return filename
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def generate_quiz_html(quiz_data, user_answers=None, score=None):
    """Generate an HTML file with quiz results that can be downloaded."""
    try:
        # Ensure the directory exists
        html_dir = os.path.join(settings.MEDIA_ROOT, "quizai_downloads")
        os.makedirs(html_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = int(time.time())
        random_str = secrets.token_hex(4)
        filename = f"quiz_{timestamp}_{random_str}.html"
        html_path = os.path.join(html_dir, filename)
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>AI Generated Quiz Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2 {{ color: #4a6bff; text-align: center; }}
                .question {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
                .options {{ margin-left: 20px; }}
                .answer {{ font-weight: bold; color: #28a745; }}
                .explanation {{ font-style: italic; color: #555; margin: 10px 0; }}
                .user-answer {{ margin-top: 10px; padding: 5px; }}
                .correct {{ color: #28a745; font-weight: bold; }}
                .incorrect {{ color: #dc3545; font-weight: bold; }}
                .score-section {{ margin: 30px auto; padding: 15px; background-color: #f8f9fa; 
                                 border-radius: 5px; text-align: center; max-width: 500px; }}
                @media print {{
                    .no-print {{ display: none; }}
                    body {{ font-size: 12pt; }}
                }}
            </style>
        </head>
        <body>
            <h1>AI Generated Quiz Results</h1>
            <p style="text-align: center;">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div class="no-print" style="text-align: center; margin: 20px 0;">
                <button onclick="window.print()">Print Quiz Results</button>
            </div>
        """
        
        # Add score if available
        if score is not None:
            percentage = (score / len(quiz_data)) * 100
            html_content += f"""
            <div class="score-section">
                <h2>Final Score: {score}/{len(quiz_data)}</h2>
                <p style="font-size: 1.2em;">Percentage: {percentage:.1f}%</p>
            </div>
            """
        
        # Add questions
        for i, q in enumerate(quiz_data):
            # Handle different formats of user_answers
            user_answer = None
            if user_answers:
                if isinstance(user_answers, list) and i < len(user_answers):
                    user_answer = user_answers[i]
                elif isinstance(user_answers, dict):
                    # Try different possible keys
                    user_answer = user_answers.get(str(i)) or user_answers.get(i) or user_answers.get(f"{i}_text")
            
            # Get correct answer
            correct_answer = q.get("correct_answer")
            if not correct_answer:
                correct_answer = q.get("answer", "")
                
            is_correct = False
            if user_answer:
                # Try different comparison methods
                if isinstance(user_answer, str) and isinstance(correct_answer, str):
                    is_correct = user_answer.upper() == correct_answer.upper()
                else:
                    is_correct = user_answer == correct_answer
                    
            result_class = "correct" if is_correct else "incorrect"
            
            html_content += f"""
            <div class="question">
                <h3>Question {i+1}: {q.get('question')}</h3>
                <div class="options">
            """
            
            # Add options
            for option in q.get("options", []):
                html_content += f"<p>{option}</p>"
            
            # Add correct answer and explanation
            html_content += f"""
                </div>
                <p class="answer">Correct Answer: {q.get('correct_answer')}</p>
            """
            
            if q.get("explanation"):
                html_content += f'<p class="explanation">Explanation: {q.get("explanation")}</p>'
            
            # Add user's answer if available
            if user_answer:
                result_text = "✓ Correct" if is_correct else "✗ Incorrect"
                html_content += f"""
                <div class="user-answer {result_class}">
                    Your Answer: {user_answer} ({result_text})
                </div>
                """
            
            html_content += "</div>"
        
        html_content += """
        <div class="no-print" style="text-align: center; margin: 20px 0;">
            <button onclick="window.print()">Print Quiz Results</button>
        </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logger.info(f"HTML file saved at: {html_path}")
        return filename
        
    except Exception as e:
        logger.error(f"HTML file generation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Initialize the quiz generator
quiz_generator = QuizGenerator()

@login_required
def index(request):
    """Landing page for the Quiz AI app"""
    context = {
        'title': 'TOBBI - The AI Quiz Creator',
        'is_admin': request.user.is_staff or request.user.is_superuser,
    }
    return render(request, 'index.html', context)

@login_required
def generate_quiz(request):
    """Generate a quiz using OpenAI API."""
    if request.method == "POST":
        try:
            topic = request.POST.get("topic")
            num_questions = int(request.POST.get("num_questions", 5))
            difficulty = request.POST.get("difficulty", "medium")
            use_fallback = request.POST.get("use_fallback", "false") == "true"
            
            if not topic:
                messages.error(request, "Topic is required")
                return redirect('quizai:generate')
            
            if num_questions < 1 or num_questions > 15:
                num_questions = 5  # Set to default if out of range
            
            quiz_questions = None
            
            # Try API first, unless fallback is explicitly requested
            if not use_fallback:
                # Initialize the generator with the API key
                generator = QuizGenerator()
                quiz_questions = generator.generate_quiz(topic, num_questions, difficulty)
            
            # If API fails or fallback is requested, use sample quiz
            if quiz_questions is None:
                if not use_fallback:
                    # Only show error message if it wasn't a deliberate fallback
                    error_message = "We're currently experiencing high demand on our quiz generation service."
                    
                    if hasattr(generator, 'last_error'):
                        if 'rate limit' in generator.last_error.lower():
                            error_message += " The API rate limit has been exceeded."
                        elif 'configuration' in generator.last_error.lower() or 'api key' in generator.last_error.lower():
                            error_message += " There's a configuration issue with our AI service."
                    
                    error_message += " We're providing you with a pre-made quiz instead."
                    messages.warning(request, error_message)
                
                # Use sample quiz as fallback
                logger.info(f"Using sample quiz for topic: {topic} (API generation failed or fallback requested)")
                quiz_questions = get_sample_quiz(topic, num_questions)
                
                if not quiz_questions:
                    messages.error(request, "Failed to generate quiz. Please try again with a different topic.")
                    return redirect('quizai:generate')
            
            # Store in session
            request.session["current_quiz"] = quiz_questions
            request.session["quiz_title"] = f"{topic} Quiz ({difficulty.capitalize()})"
            request.session["quiz_id"] = str(uuid.uuid4())
            
            # Save to database if we want to persist quizzes
            if getattr(settings, 'SAVE_AI_QUIZZES', False):
                try:
                    quiz = AIQuiz.objects.create(
                        title=f"{topic} Quiz ({difficulty.capitalize()})",
                        questions_json=json.dumps(quiz_questions)
                    )
                    request.session["quiz_id"] = str(quiz.id)
                except Exception as e:
                    logger.error(f"Error saving quiz to database: {e}")
            
            # Redirect to start the quiz
            return redirect('quizai:start_quiz')
            
        except Exception as e:
            logger.error(f"Generate quiz error: {e}")
            messages.error(request, f"Error generating quiz: {str(e)}")
            return redirect('quizai:generate')
    
    return render(request, "QuizAiApp/generate.html")

@login_required
def edit_quiz(request):
    """Edit an existing quiz based on user feedback."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            edit_prompt = data.get("edit_prompt", "")
            
            if not edit_prompt:
                return JsonResponse({"error": "Please provide instructions for editing"}, status=400)
            
            current_quiz = request.session.get("current_quiz", [])
            if not current_quiz:
                return JsonResponse({"error": "No quiz found to edit"}, status=400)
            
            # Edit the quiz
            result = quiz_generator.edit_quiz(current_quiz, edit_prompt)
            
            if "error" in result:
                return JsonResponse(result, status=500)
            
            # Update session
            request.session["current_quiz"] = result["questions"]
            
            return JsonResponse(result)
        
        except Exception as e:
            logger.error(f"Edit quiz error: {e}")
            return JsonResponse({"error": f"Failed to edit quiz: {str(e)}"}, status=500)
    
    current_quiz = request.session.get("current_quiz", [])
    if not current_quiz:
        return redirect('quizai:index')
    
    return render(request, 'QuizAiApp/edit.html')

@login_required
def start_quiz(request):
    """Start a quiz session with the current quiz."""
    # Check if a quiz_id was passed in the URL
    quiz_id = request.GET.get('quiz_id')
    
    if quiz_id:
        try:
            # Try to load the quiz from the database using the Quiz model
            from QuizTemplateApp.models import Quiz
            quiz = Quiz.objects.get(id=quiz_id)
            
            # Convert quiz questions to the format expected by the quiz template
            questions = []
            for question in quiz.questions.all():
                # Get the choices for this question
                choices = question.choices.all()
                correct_choice = choices.filter(is_correct=True).first()
                
                # Format the question for the template
                formatted_question = {
                    "question": question.question_text,
                    "options": [choice.choice_text for choice in choices],
                    "correct_answer": correct_choice.choice_text if correct_choice else ""
                }
                questions.append(formatted_question)
            
            # Store in session
            request.session["current_quiz"] = questions
            request.session["quiz_title"] = quiz.title
            request.session["quiz_id"] = str(quiz.id)
            
            # Reset user answers
            request.session["user_answers"] = []
            request.session["current_question_index"] = 0
            
            # Store start time for time tracking
            from django.utils import timezone
            request.session["quiz_start_time"] = timezone.now().isoformat()
            
            # Otherwise render the quiz.html template
            return render(request, 'QuizAiApp/quiz.html', {
                'quiz': questions,
                'quiz_title': quiz.title,
                'total_questions': len(questions)
            })
        except Exception as e:
            logger.error(f"Error loading quiz with ID {quiz_id}: {e}")
            messages.error(request, f"Error loading quiz: {str(e)}")
            return redirect('quizai:generate')
    
    # If no quiz_id or loading failed, fall back to session data
    current_quiz = request.session.get("current_quiz", [])
    
    if not current_quiz:
        messages.error(request, "No quiz generated yet. Please create a quiz first.")
        return redirect('quizai:generate')
    
    # Reset user answers
    request.session["user_answers"] = []
    request.session["current_question_index"] = 0
    
    # Store start time for time tracking
    from django.utils import timezone
    request.session["quiz_start_time"] = timezone.now().isoformat()
    
    quiz_title = request.session.get("quiz_title", "AI Generated Quiz")
    
    # If using AJAX for quiz, return first question as JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        first_question = current_quiz[0]
        return JsonResponse({
            "question": first_question["question"],
            "options": first_question["options"],
            "current_index": 0,
            "total_questions": len(current_quiz)
        })
    
    # Otherwise render the quiz.html template
    return render(request, 'QuizAiApp/quiz.html', {
        'quiz': current_quiz,
        'quiz_title': quiz_title,
        'total_questions': len(current_quiz)
    })

@login_required
def next_question(request):
    """Process the current answer and move to the next question."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        answer = data.get("answer")
        question_index = int(data.get("question_index", 0))
        
        current_quiz = request.session.get("current_quiz", [])
        user_answers = request.session.get("user_answers", [])
        
        # Store the answer in user_answers
        while len(user_answers) <= question_index:
            user_answers.append(None)
            
        user_answers[question_index] = answer
        request.session["user_answers"] = user_answers
        
        # Check if this was the last question
        next_index = question_index + 1
        if next_index >= len(current_quiz):
            return JsonResponse({"completed": True})
        
        request.session["current_question_index"] = next_index
        return JsonResponse({
            "next_index": next_index,
            "total_questions": len(current_quiz)
        })
    
    except Exception as e:
        logger.error(f"Next question error: {e}")
        return JsonResponse({"error": f"Error processing question: {str(e)}"}, status=500)

@login_required
def finish_quiz(request):
    """Calculate and return the final score."""
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        # Handle both form data and JSON requests
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                # Add JSON data to POST-like structure
                request.POST = request.POST.copy()  # Make it mutable
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        request.POST[key] = json.dumps(value)
                    else:
                        request.POST[key] = value
                logger.info(f"Processed JSON request with keys: {list(data.keys())}")
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON request body")
        
        # Get quiz data from session
        current_quiz = request.session.get('current_quiz', [])
        if not current_quiz:
            return JsonResponse({"error": "No active quiz found"}, status=400)
        
        # Get user answers from request or session
        user_answers_json = request.POST.get('answers', '{}')
        user_answers = json.loads(user_answers_json) if user_answers_json else {}
        
        # If POST contains 'user_answers' field, use that (extended format with indices and text)
        if 'user_answers' in request.POST:
            try:
                extended_answers = json.loads(request.POST.get('user_answers', '{}'))
                # Convert the extended format to the simple format expected by the scoring logic
                if extended_answers:
                    for q_idx, answer_data in extended_answers.items():
                        # Store both the index and text versions to increase match chances
                        user_answers[q_idx] = answer_data.get('index')
                        user_answers[f"{q_idx}_text"] = answer_data.get('text')
                logger.info(f"Processed extended user answers format: {len(extended_answers)} answers")
            except Exception as e:
                logger.error(f"Error processing extended user answers: {e}")
        
        # If no answers in POST, try to get them from session
        if not user_answers and request.session.get('user_answers'):
            user_answers = {str(i): ans for i, ans in enumerate(request.session.get('user_answers'))}
        
        start_time = request.POST.get('start_time') or request.session.get('quiz_start_time')
        quiz_id = request.POST.get('quiz_id') or request.session.get('quiz_id', str(uuid.uuid4()))
        quiz_title = request.POST.get('quiz_title') or request.session.get('quiz_title', 'AI Generated Quiz')
        
        # Calculate score
        score = 0
        attempt_data = {
            'questions': [],
            'total_questions': len(current_quiz),
            'correct_answers': 0,
            'incorrect_answers': 0,
            'skipped_questions': 0,
            'time_taken': None,
            'start_time': start_time,
            'end_time': timezone.now().isoformat()
        }
        
        for i, question in enumerate(current_quiz):
            # Use index as question_id if not present
            question_id = str(i)
            
            # Get user's answer for this question (check multiple formats)
            user_answer = None
            user_answer_text = None
            
            # Check numeric index answers
            if question_id in user_answers:
                user_answer = user_answers[question_id]
            elif str(i) in user_answers:
                user_answer = user_answers[str(i)]
            elif i < len(request.session.get('user_answers', [])):
                user_answer = request.session['user_answers'][i]
                
            # Check text answers 
            if f"{question_id}_text" in user_answers:
                user_answer_text = user_answers[f"{question_id}_text"]
            
            # Get correct answer - check all possible keys where it might be stored
            correct_answer = None
            correct_answer_index = None
            
            # Try to get the correct answer from various possible formats
            if 'correct_answer' in question:
                correct_answer = question.get('correct_answer')
            elif 'answer' in question:
                correct_answer = question.get('answer')
            elif 'correctAnswer' in question:  # JavaScript camelCase format
                correct_answer_index = question.get('correctAnswer')
                # If it's an index, convert to the actual text answer
                if isinstance(correct_answer_index, int) and 'options' in question:
                    options = question.get('options', [])
                    if 0 <= correct_answer_index < len(options):
                        correct_answer = options[correct_answer_index]
            
            # Skip if no correct answer found
            if correct_answer is None and correct_answer_index is None:
                logger.warning(f"Question {i} has no correct answer: {question}")
                continue
                
            # Create question data for the attempt
            question_data = {
                'id': question_id,
                'question': question['question'],
                'options': question.get('options', []),
                'correct_answer': correct_answer,
                'correct_answer_index': correct_answer_index,
                'user_answer': user_answer,
                'user_answer_text': user_answer_text,
                'is_correct': False,
                'time_taken': None
            }
            
            # Check if answer is correct - handle multiple formats
            is_correct = False
            
            if user_answer is not None or user_answer_text is not None:
                # Case 1: Direct index comparison (both are numeric indices)
                if correct_answer_index is not None and isinstance(user_answer, (int, str)) and str(user_answer).isdigit():
                    if int(user_answer) == correct_answer_index:
                        is_correct = True
                        
                # Case 2: Text answer comparison
                elif correct_answer is not None:
                    # Try exact match (case insensitive)
                    if user_answer_text and user_answer_text.upper() == correct_answer.upper():
                        is_correct = True
                    elif user_answer is not None and not isinstance(user_answer, (int, float)) and user_answer.upper() == correct_answer.upper():
                        is_correct = True
                    # For full text answers, check if one contains the other
                    elif user_answer_text and len(user_answer_text) > 1 and len(correct_answer) > 1:
                        if user_answer_text.upper() in correct_answer.upper() or correct_answer.upper() in user_answer_text.upper():
                            is_correct = True
                    elif user_answer and not isinstance(user_answer, (int, float)) and len(user_answer) > 1 and len(correct_answer) > 1:
                        if user_answer.upper() in correct_answer.upper() or correct_answer.upper() in user_answer.upper():
                            is_correct = True
                    # For single letter answers, try to match first letter
                    elif user_answer_text and len(user_answer_text) == 1 and len(correct_answer) > 1:
                        if user_answer_text.upper() == correct_answer[0].upper():
                            is_correct = True
                    elif user_answer and not isinstance(user_answer, (int, float)) and len(user_answer) == 1 and len(correct_answer) > 1:
                        if user_answer.upper() == correct_answer[0].upper():
                            is_correct = True
                
                # Case 3: If we have an index-based user answer and options are available
                elif correct_answer_index is not None and 'options' in question:
                    options = question.get('options', [])
                    if isinstance(user_answer, (int, str)) and str(user_answer).isdigit():
                        user_idx = int(user_answer)
                        if user_idx == correct_answer_index:
                            is_correct = True
                
                if is_correct:
                    score += 1
                    question_data['is_correct'] = True
                    attempt_data['correct_answers'] += 1
                else:
                    attempt_data['incorrect_answers'] += 1
            else:
                attempt_data['skipped_questions'] += 1
            
            attempt_data['questions'].append(question_data)
        
        # Calculate time taken if start_time is provided
        time_taken = None
        if start_time:
            try:
                start_time_dt = None
                if isinstance(start_time, str):
                    start_time_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_time = timezone.now()
                time_taken = end_time - start_time_dt if start_time_dt else None
                if time_taken:
                    attempt_data['time_taken'] = str(time_taken)
            except Exception as e:
                logger.error(f"Time calculation error: {e}")
        
        # Save to AIQuizAttempt if user is authenticated
        if request.user.is_authenticated:
            try:
                # Ensure quiz_id is valid
                if not quiz_id or quiz_id == 'None':
                    quiz_id = str(uuid.uuid4())
                    logger.info(f"Generated new quiz_id: {quiz_id}")
                else:
                    logger.info(f"Using existing quiz_id: {quiz_id}")
                
                # Check if we can find an existing quiz with this ID in the user's quizzes
                try:
                    from QuizTemplateApp.models import Quiz
                    user_quizzes = Quiz.objects.filter(created_by=request.user)
                    
                    # First try to find a quiz with matching ID
                    matching_quiz = user_quizzes.filter(id=quiz_id).first()
                    
                    # If not found, try to find a quiz with matching title
                    if not matching_quiz:
                        for quiz in user_quizzes:
                            if quiz_title.lower() in quiz.title.lower() or quiz.title.lower() in quiz_title.lower():
                                matching_quiz = quiz
                                quiz_id = str(matching_quiz.id)
                                logger.info(f"Found quiz with matching title: {matching_quiz.title}, using ID: {quiz_id}")
                                break
                    
                    # If still not found and we have quizzes, use the most recent
                    if not matching_quiz and user_quizzes.exists():
                        matching_quiz = user_quizzes.order_by('-created_at').first()
                        quiz_id = str(matching_quiz.id)
                        logger.info(f"Using most recent quiz: {matching_quiz.title}, ID: {quiz_id}")
                    
                except Exception as e:
                    logger.warning(f"Error checking for existing quizzes: {e}")
                
                # Create attempt record with attempt_data
                attempt = AIQuizAttempt.objects.create(
                    user=request.user,
                    quiz_id=quiz_id,
                    quiz_title=quiz_title,
                    score=score,
                    max_score=len(current_quiz),
                    completed=True,
                    completed_at=timezone.now(),
                    time_taken=time_taken,
                    attempt_data=attempt_data  # Store as JSON (Django handles JSON conversion)
                )
                logger.info(f"Quiz attempt saved for user {request.user.username}, score: {score}/{len(current_quiz)}, quiz_id: {quiz_id}")
            except Exception as e:
                logger.error(f"Error saving quiz attempt: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Clear quiz from session to prevent duplicate submissions
        if 'current_quiz' in request.session:
            del request.session['current_quiz']
        if 'user_answers' in request.session:
            del request.session['user_answers']
        if 'quiz_start_time' in request.session:
            del request.session['quiz_start_time']
        if 'quiz_id' in request.session:
            del request.session['quiz_id']
        if 'quiz_title' in request.session:
            del request.session['quiz_title']
        
        # Generate HTML file for download
        html_filename = generate_quiz_html(current_quiz, user_answers, score)
        file_url = None
        file_type = None
        
        if html_filename:
            file_url = f"{settings.MEDIA_URL}quizai_downloads/{html_filename}"
            file_type = "html"
            logger.info(f"Generated download file: {file_url}")
        
        return JsonResponse({
            "score": score,
            "total": len(current_quiz),
            "attempt_data": attempt_data,
            "file_url": file_url,
            "file_type": file_type
        })
        
    except Exception as e:
        logger.error(f"Error in finish_quiz: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def download_quiz(request):
    """Generate and provide a download link for the quiz PDF."""
    try:
        # Get quiz attempt ID or quiz ID from query parameters
        attempt_id = request.GET.get('attempt_id')
        quiz_id = request.GET.get('quiz_id')
        
        current_quiz = []
        user_answers = []
        score = None
        quiz_title = "AI Generated Quiz"
        
        from QuizTemplateApp.models import AIQuizAttempt
        
        if attempt_id:
            # Load specific quiz attempt by ID
            try:
                attempt = AIQuizAttempt.objects.get(id=attempt_id, user=request.user)
                quiz_id = attempt.quiz_id
                score = attempt.score
                user_answers = []
                
                logger.info(f"Found attempt: {attempt.id} with quiz_id: {quiz_id}")
                
                # Check for quiz_data in attempt_data
                if attempt.attempt_data and isinstance(attempt.attempt_data, dict):
                    logger.info(f"Attempt data found: {attempt.attempt_data.keys()}")
                    
                    # First check if we have a 'questions' key directly
                    if 'questions' in attempt.attempt_data:
                        current_quiz = attempt.attempt_data['questions']
                        logger.info(f"Found {len(current_quiz)} questions in attempt_data['questions']")
                        
                        # Extract user answers if available
                        for q in current_quiz:
                            user_answers.append(q.get('user_answer') or q.get('user_answer_text'))
                
                # If no questions found or questions is empty, use attempt_data itself as the current_quiz
                if not current_quiz and attempt.attempt_data:
                    # Try common formats for question data in attempt_data
                    if isinstance(attempt.attempt_data, list):
                        current_quiz = attempt.attempt_data
                        logger.info(f"Using attempt_data list as quiz data: {len(current_quiz)} items")
                    elif isinstance(attempt.attempt_data, dict) and 'total_questions' in attempt.attempt_data:
                        logger.info("Reconstructing quiz from attempt_data")
                        reconstructed_quiz = []
                        if 'questions' in attempt.attempt_data:
                            for q_data in attempt.attempt_data['questions']:
                                q_item = {
                                    'question': q_data.get('question', 'Unknown question'),
                                    'options': q_data.get('options', []),
                                    'correct_answer': q_data.get('correct_answer', ''),
                                    'explanation': q_data.get('explanation', '')
                                }
                                reconstructed_quiz.append(q_item)
                            if reconstructed_quiz:
                                current_quiz = reconstructed_quiz
                                logger.info(f"Reconstructed {len(current_quiz)} questions from attempt_data")
                                
                # If still no questions, try Quiz model instead
                if not current_quiz and quiz_id:
                    try:
                        from QuizTemplateApp.models import Quiz
                        try:
                            standard_quiz = Quiz.objects.get(id=quiz_id)
                            # Convert standard quiz format to AI quiz format
                            for question in standard_quiz.questions.all():
                                choices = list(question.choices.all().values_list('choice_text', flat=True))
                                correct_choice = question.choices.filter(is_correct=True).first()
                                current_quiz.append({
                                    'question': question.question_text,
                                    'options': choices,
                                    'correct_answer': correct_choice.choice_text if correct_choice else ''
                                })
                            quiz_title = standard_quiz.title
                            logger.info(f"Loaded standard quiz: {standard_quiz.title} with {len(current_quiz)} questions")
                        except Quiz.DoesNotExist:
                            logger.info(f"Regular Quiz with ID {quiz_id} not found, trying AIQuiz")
                            try:
                                ai_quiz = AIQuiz.objects.get(id=quiz_id)
                                quiz_title = ai_quiz.title
                                current_quiz = json.loads(ai_quiz.questions_json)
                                logger.info(f"Loaded AI quiz from database: {ai_quiz.title} with {len(current_quiz)} questions")
                            except AIQuiz.DoesNotExist:
                                logger.warning(f"Neither Quiz nor AIQuiz found with ID {quiz_id}")
                    except Exception as e:
                        logger.error(f"Error loading quiz for attempt: {e}")
                        # Continue with empty quiz rather than returning error
                
                logger.info(f"Successfully loaded quiz attempt {attempt_id} with {len(current_quiz)} questions")
                
            except AIQuizAttempt.DoesNotExist:
                logger.error(f"Quiz attempt {attempt_id} not found for user {request.user.username}")
                return JsonResponse({"error": "Quiz attempt not found"}, status=404)
            except Exception as e:
                logger.error(f"Error loading quiz attempt {attempt_id}: {e}")
                return JsonResponse({"error": f"Error loading quiz attempt: {str(e)}"}, status=500)
                
        elif quiz_id:
            # Load quiz by quiz ID without user answers
            try:
                # First try regular Quiz model
                from QuizTemplateApp.models import Quiz
                try:
                    standard_quiz = Quiz.objects.get(id=quiz_id)
                    # Convert standard quiz format to AI quiz format
                    for question in standard_quiz.questions.all():
                        choices = list(question.choices.all().values_list('choice_text', flat=True))
                        correct_choice = question.choices.filter(is_correct=True).first()
                        current_quiz.append({
                            'question': question.question_text,
                            'options': choices,
                            'correct_answer': correct_choice.choice_text if correct_choice else ''
                        })
                    quiz_title = standard_quiz.title
                    logger.info(f"Loaded standard quiz: {standard_quiz.title} with {len(current_quiz)} questions")
                except Quiz.DoesNotExist:
                    # Then try AIQuiz model
                    try:
                        ai_quiz = AIQuiz.objects.get(id=quiz_id)
                        quiz_title = ai_quiz.title
                        current_quiz = json.loads(ai_quiz.questions_json)
                        logger.info(f"Loaded AI quiz: {ai_quiz.title} with {len(current_quiz)} questions")
                    except AIQuiz.DoesNotExist:
                        logger.error(f"No quiz found with ID {quiz_id}")
                        return JsonResponse({"error": f"No quiz found with ID {quiz_id}"}, status=404)
            except Exception as e:
                logger.error(f"Error loading quiz {quiz_id}: {e}")
                
                # Try one more fallback - check session
                if 'current_quiz' in request.session and request.session['current_quiz']:
                    current_quiz = request.session['current_quiz']
                    quiz_title = request.session.get('quiz_title', 'AI Generated Quiz')
                    logger.info(f"Fallback to session quiz: {len(current_quiz)} questions")
                else:
                    # Create a simple default quiz rather than failing
                    current_quiz = [
                        {
                            'question': 'Quiz content could not be loaded. This is a placeholder question.',
                            'options': ['A. Option 1', 'B. Option 2', 'C. Option 3', 'D. Option 4'],
                            'correct_answer': 'A'
                        }
                    ]
                    logger.warning(f"Using placeholder quiz after load error: {str(e)}")
        else:
            # Fallback to session data
            current_quiz = request.session.get("current_quiz", [])
            user_answers = request.session.get("user_answers", [])
            quiz_title = request.session.get("quiz_title", "AI Generated Quiz")
            
            if current_quiz:
                logger.info(f"Loaded {len(current_quiz)} questions from session")
            else:
                # No current quiz, try to get the most recent attempt
                logger.info("No quiz in session, trying most recent attempt")
                recent_attempt = AIQuizAttempt.objects.filter(
                    user=request.user,
                    completed=True
                ).order_by('-completed_at').first()
                
                if recent_attempt:
                    logger.info(f"Found recent attempt {recent_attempt.id}")
                    try:
                        # First try to reconstruct from attempt_data
                        if recent_attempt.attempt_data and isinstance(recent_attempt.attempt_data, dict):
                            if 'questions' in recent_attempt.attempt_data:
                                current_quiz = recent_attempt.attempt_data['questions']
                                score = recent_attempt.score
                                quiz_title = recent_attempt.quiz_title
                                logger.info(f"Reconstructed quiz from recent attempt with {len(current_quiz)} questions")
                        
                        # If that didn't work, try to load from AIQuiz
                        if not current_quiz and recent_attempt.quiz_id:
                            try:
                                quiz = AIQuiz.objects.get(id=recent_attempt.quiz_id)
                                quiz_title = quiz.title
                                current_quiz = json.loads(quiz.questions_json)
                                score = recent_attempt.score
                                logger.info(f"Loaded quiz from database: {quiz.title} with {len(current_quiz)} questions")
                            except AIQuiz.DoesNotExist:
                                # Try standard Quiz model
                                from QuizTemplateApp.models import Quiz
                                try:
                                    standard_quiz = Quiz.objects.get(id=recent_attempt.quiz_id)
                                    # Convert standard quiz format to AI quiz format
                                    for question in standard_quiz.questions.all():
                                        choices = list(question.choices.all().values_list('choice_text', flat=True))
                                        correct_choice = question.choices.filter(is_correct=True).first()
                                        current_quiz.append({
                                            'question': question.question_text,
                                            'options': choices,
                                            'correct_answer': correct_choice.choice_text if correct_choice else ''
                                        })
                                    quiz_title = standard_quiz.title
                                    logger.info(f"Loaded standard quiz: {standard_quiz.title} with {len(current_quiz)} questions")
                                except Quiz.DoesNotExist:
                                    logger.warning(f"Neither AIQuiz nor Quiz found with ID {recent_attempt.quiz_id}")
                                    # Create placeholder quiz data
                                    current_quiz = [
                                        {
                                            'question': 'Quiz content could not be loaded. This is a placeholder question.',
                                            'options': ['A. Option 1', 'B. Option 2', 'C. Option 3', 'D. Option 4'],
                                            'correct_answer': 'A'
                                        }
                                    ]
                                    quiz_title = "Quiz Content Unavailable"
                    except Exception as e:
                        logger.error(f"Failed to load quiz from database: {e}")
                        # Create placeholder quiz data
                        current_quiz = [
                            {
                                'question': 'Quiz content could not be loaded. This is a placeholder question.',
                                'options': ['A. Option 1', 'B. Option 2', 'C. Option 3', 'D. Option 4'],
                                'correct_answer': 'A'
                            }
                        ]
                        quiz_title = "Quiz Content Unavailable"
                else:
                    logger.warning("No recent attempts found")
                    return JsonResponse({"error": "No quiz found to download"}, status=400)
        
        # Ensure current_quiz is not empty (better to show placeholder than error)
        if not current_quiz:
            logger.warning("Quiz data is empty, using placeholder")
            current_quiz = [
                {
                    'question': 'Quiz content could not be loaded. This is a placeholder question.',
                    'options': ['A. Option 1', 'B. Option 2', 'C. Option 3', 'D. Option 4'],
                    'correct_answer': 'A'
                }
            ]
        
        logger.info(f"Generating PDF for quiz with {len(current_quiz)} questions")
        
        # Calculate score if not already set
        if score is None and user_answers:
            score = 0
            for i, q in enumerate(current_quiz):
                if i < len(user_answers) and user_answers[i] == q.get("correct_answer"):
                    score += 1
        
        # Generate PDF directly
        pdf_filename = generate_quiz_pdf(current_quiz, user_answers, score)
        
        if not pdf_filename:
            logger.error("Failed to generate PDF")
            return JsonResponse({"error": "Failed to generate download file"}, status=500)
        
        # Return the PDF URL
        file_url = f"{settings.MEDIA_URL}quizai_downloads/{pdf_filename}"
        file_type = "pdf" if pdf_filename.endswith(".pdf") else "html"
        logger.info(f"Download URL: {file_url} (type: {file_type})")
        
        # If this is a direct browser request, redirect to the file
        if request.headers.get('Accept', '').startswith('application/pdf') or request.headers.get('Accept', '').startswith('text/html'):
            return redirect(file_url)
            
        return JsonResponse({
            "file_url": file_url,
            "file_type": file_type
        })
    
    except Exception as e:
        logger.error(f"Download quiz error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Create a placeholder PDF rather than returning an error
        try:
            placeholder_quiz = [
                {
                    'question': 'Quiz content could not be loaded due to an error. This is a placeholder question.',
                    'options': ['A. Option 1', 'B. Option 2', 'C. Option 3', 'D. Option 4'],
                    'correct_answer': 'A',
                    'explanation': f'Error details: {str(e)}'
                }
            ]
            pdf_filename = generate_quiz_pdf(placeholder_quiz, None, None)
            if pdf_filename:
                file_url = f"{settings.MEDIA_URL}quizai_downloads/{pdf_filename}"
                return redirect(file_url)
        except Exception as fallback_error:
            logger.error(f"Even fallback PDF generation failed: {fallback_error}")
            
        return JsonResponse({"error": f"Error generating download: {str(e)}"}, status=500)

@login_required
def check_media_access(request):
    """Diagnostic endpoint to check if media files can be generated and accessed."""
    try:
        # Create a simple test file
        test_dir = os.path.join(settings.MEDIA_ROOT, "quizai_downloads")
        os.makedirs(test_dir, exist_ok=True)
        
        test_filename = f"test_{int(time.time())}.txt"
        test_path = os.path.join(test_dir, test_filename)
        
        with open(test_path, 'w') as f:
            f.write(f"Media test file created at {datetime.now()}")
        
        # Get absolute file path and URL
        abs_path = os.path.abspath(test_path)
        rel_url = f"{settings.MEDIA_URL}quizai_downloads/{test_filename}"
        
        media_info = {
            "media_root": settings.MEDIA_ROOT,
            "media_url": settings.MEDIA_URL,
            "test_file_path": abs_path,
            "test_file_url": rel_url,
            "file_exists": os.path.exists(test_path),
            "server_time": str(datetime.now())
        }
        
        return JsonResponse({
            "status": "success",
            "message": "Media diagnostic complete",
            "media_info": media_info
        })
    
    except Exception as e:
        logger.error(f"Media diagnostic error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            "status": "error",
            "message": f"Media diagnostic failed: {str(e)}",
            "traceback": traceback.format_exc()
        }, status=500) 