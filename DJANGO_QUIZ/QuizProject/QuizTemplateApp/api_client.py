import requests
from django.conf import settings

class FlaskAPIClient:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:5000'  # Flask API base URL
        self.token = None

    def register(self, name, email, mobile, password):
        url = f"{self.base_url}/registerapi"
        data = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "password": password
        }
        response = requests.post(url, json=data)
        return response.json()

    def login(self, email, password):
        url = f"{self.base_url}/loginapi"
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json()['access_token']
        return response.json()

    def get_profile(self):
        if not self.token:
            raise Exception("Not logged in")
        
        url = f"{self.base_url}/profile"
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)
        return response.json()