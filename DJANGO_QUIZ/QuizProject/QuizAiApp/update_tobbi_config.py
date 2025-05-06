import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizProject.settings')
django.setup()

from QuizAiApp.models import TobbiAPIConfig

# Define a new working configuration
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "deepseek/deepseek-r1:free"  # Alternative model

# Update or create the configuration
try:
    # Get the active config
    config = TobbiAPIConfig.objects.filter(is_active=True).first()
    
    if config:
        # Update the existing configuration
        config.api_key = API_KEY
        config.base_url = BASE_URL
        config.model = MODEL
        config.save()
        print(f"Updated existing TOBBI API config: {config}")
    else:
        # Create a new configuration
        config = TobbiAPIConfig.objects.create(
            api_key=API_KEY,
            base_url=BASE_URL,
            model=MODEL,
            is_active=True
        )
        print(f"Created new TOBBI API config: {config}")
    
    print(f"API Key: {API_KEY[:5]}***")
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    
except Exception as e:
    print(f"Error updating TOBBI API config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("TOBBI API configuration updated successfully") 