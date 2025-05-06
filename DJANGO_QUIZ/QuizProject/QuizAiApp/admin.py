from django.contrib import admin
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .models import AIQuiz, TobbiAPIConfig
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

@admin.register(AIQuiz)
class AIQuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(TobbiAPIConfig)
class TobbiAPIConfigAdmin(admin.ModelAdmin):
    list_display = ('model', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'model')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('api_key', 'base_url', 'model', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test-tobbi-api/', 
                 self.admin_site.admin_view(self.test_tobbi_api_view), 
                 name='tobbiapiconfig_test_api'),
        ]
        return custom_urls + urls
    
    @method_decorator(csrf_protect)
    def test_tobbi_api_view(self, request):
        """Admin view to test the TOBBI API"""
        context = {
            **self.admin_site.each_context(request),
            'title': 'Test TOBBI API Connection',
            'opts': self.model._meta,
            'app_label': 'QuizAiApp',
            'model_name': 'tobbiapiconfig',
            'changelist_url': '/admin/QuizAiApp/tobbiapiconfig/'
        }
        
        # For both GET and POST, check if there's an active configuration
        api_config = TobbiAPIConfig.objects.filter(is_active=True).first()
        if api_config:
            context['api_config_exists'] = True
            context['api_key_preview'] = api_config.api_key[:5] + '***' if api_config.api_key else 'No API key set'
            context['base_url'] = api_config.base_url
            context['model'] = api_config.model
        else:
            context['api_config_exists'] = False
            context['warning'] = "There is no active TOBBI API configuration. Please create and activate a configuration before testing."
            
        if request.method == 'POST':
            # Log that we received a POST request
            logger.info("Received POST request to test TOBBI API")
            
            try:
                # Check if we have a configuration
                if not api_config:
                    context['error'] = "No active TOBBI API configuration found. Please create and activate a configuration first."
                    return TemplateResponse(request, 'admin/quizai/test_tobbi_api.html', context)
                
                # Basic validation
                if not api_config.api_key:
                    context['error'] = "The API key is empty. Please add a valid API key to your configuration."
                    return TemplateResponse(request, 'admin/quizai/test_tobbi_api.html', context)
                
                # Log the API details for debugging
                logger.info(f"Testing API with key: {api_config.api_key[:5]}*** at URL: {api_config.base_url}")
                
                # Initialize OpenAI client with additional parameters for better diagnostics
                try:
                    client = OpenAI(
                        base_url=api_config.base_url,
                        api_key=api_config.api_key,
                        timeout=30.0  # Increase timeout for slow connections
                    )
                    logger.info("OpenAI client initialized successfully")
                except Exception as client_error:
                    logger.error(f"Failed to initialize OpenAI client: {str(client_error)}")
                    context['error'] = f"Failed to initialize API client: {str(client_error)}"
                    return TemplateResponse(request, 'admin/quizai/test_tobbi_api.html', context)
                
                # Test prompt with error handling
                try:
                    logger.info(f"Sending test request to model: {api_config.model}")
                    response = client.chat.completions.create(
                        model=api_config.model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "Hello, TOBBI! Give me a brief 1-sentence response."}
                        ],
                        max_tokens=50
                    )
                    logger.info("API request successful")
                except Exception as api_error:
                    logger.error(f"API request failed: {str(api_error)}")
                    context['error'] = f"API request failed: {str(api_error)}"
                    return TemplateResponse(request, 'admin/quizai/test_tobbi_api.html', context)
                
                # Extract content and update context
                try:
                    content = response.choices[0].message.content
                    logger.info(f"API test successful! Response: {content}")
                    
                    context['success'] = True
                    context['response'] = content
                    context['model_used'] = api_config.model
                    context['full_response'] = str(response)
                except Exception as parse_error:
                    logger.error(f"Failed to parse API response: {str(parse_error)}")
                    context['error'] = f"Failed to parse API response: {str(parse_error)}"
                    
            except Exception as e:
                logger.error(f"Unexpected error testing TOBBI API: {str(e)}")
                context['error'] = f"Unexpected error: {str(e)}"
        
        # Return the template response
        return TemplateResponse(request, 'admin/quizai/test_tobbi_api.html', context)
    
    def save_model(self, request, obj, form, change):
        """When saving a model, show a message if the API key is invalid"""
        super().save_model(request, obj, form, change)
        if obj.is_active:
            self.message_user(request, f"Configuration '{obj}' is now active.")
