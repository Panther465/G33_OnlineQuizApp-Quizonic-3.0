from flask import Flask, request
from flask_restful import Api, Resource
from models import db
from models.model import User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

jwt = JWTManager()

class UserRegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            print("Received registration data:", data)  # Debug print
            
            # Validate data
            if not data:
                return {"message": "No data provided"}, 400
                
            name = data.get("name")
            email = data.get("email")
            mobile = data.get("mobile")
            password = data.get("password")
            
            # Validate required fields
            if not all([name, email, mobile, password]):
                return {"message": "All fields are required"}, 400
                
            # Check if email exists
            if User.query.filter_by(email=email).first():
                return {"message": "Email already exists"}, 400
                
            # Create user
            user = User(name=name, email=email, mobile=mobile, role="user")
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {"message": "Registration successful"}, 201
            
        except Exception as e:
            print("Registration error:", str(e))  # Debug print
            db.session.rollback()
            return {"message": "Registration failed"}, 500

class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            }, 200

        return {"message": "Invalid credentials."}, 401

class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {"message": "User not found."}, 404
            
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "mobile": user.mobile,
                "role": user.role
            }
        }, 200 