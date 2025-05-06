from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

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