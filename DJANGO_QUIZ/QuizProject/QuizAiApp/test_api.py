import os
import sys
import json
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizProject.settings')
django.setup()

from QuizAiApp.models import TobbiAPIConfig
from openai import OpenAI

# Get the active configuration
try:
    config = TobbiAPIConfig.objects.filter(is_active=True).first()
    if config:
        API_KEY = config.api_key
        BASE_URL = config.base_url
        MODEL = config.model
        print(f"Found active TOBBI API config with model: {MODEL}")
        print(f"API Key (preview): {API_KEY[:5]}***")
    else:
        # Default values from views.py
        API_KEY = "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"
        BASE_URL = "https://openrouter.ai/api/v1"
        MODEL = "deepseek/deepseek-r1:free"
        print("No active TOBBI API config found, using defaults:")
        print(f"API Key: {API_KEY[:5]}***")
        print(f"Base URL: {BASE_URL}")
        print(f"Model: {MODEL}")
except Exception as e:
    print(f"Error getting TOBBI API config: {e}")
    sys.exit(1)

# Initialize the OpenAI client
try:
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )
    print("Successfully initialized OpenAI client")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    sys.exit(1)

# Test prompt
try:
    print(f"Sending test request to model: {MODEL}")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
            {"role": "user", "content": "Hello, TOBBI! Generate a simple 2-question quiz about science in JSON format with questions that have 4 options (A, B, C, D) and a correct answer."}
        ],
        max_tokens=500,
        response_format={"type": "json_object"}
    )
    print("API request successful!")
    
    # Print the response
    if hasattr(response, 'choices') and response.choices:
        content = response.choices[0].message.content
        print("\nResponse content:")
        print(content)
        
        # Process content - clean up any markdown code blocks
        if isinstance(content, str):
            content = content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
        
        # Try parsing as JSON
        try:
            json_data = json.loads(content)
            print("\nParsed JSON successfully!")
            print(json.dumps(json_data, indent=2))
        except json.JSONDecodeError as e:
            print(f"\nCould not parse content as JSON: {e}")
            print("Trying to fix JSON...")
            
            # Try to find JSON in the string
            import re
            json_pattern = r'\{.*\}'
            json_match = re.search(json_pattern, content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    fixed_json = json.loads(json_str)
                    print("Fixed JSON successfully!")
                    print(json.dumps(fixed_json, indent=2))
                except:
                    print("Still couldn't parse JSON after fixing")
    else:
        print("Response doesn't contain expected 'choices' structure")
        print(f"Full response: {response}")
except Exception as e:
    print(f"Error testing API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAPI test completed successfully") 