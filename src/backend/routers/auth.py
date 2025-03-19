from typing import Any
from fastapi import APIRouter, Depends, Request
from models import user
from models.user import User, UserBase , UserInDB, UserLogin
from dependencies.auth import get_current_user
from database.cloud_db_controller import CloudDBController
from datetime import datetime
router = APIRouter(
    prefix="/api",
    tags=["auth"],
    responses={404: {"description": "Not found"},
               401: {"description": "Unauthorized"},
               403: {"description": "Forbidden"},
               500: {"description": "Server Error"},
               200: {"description": "Success"}}
)

@router.post("/login/")
async def login(request: Request):
    # Logic for user login
    user = await request.json()
    
    print(user)
    
    # Initialize the database controller
    db_controller = CloudDBController()
    
    # Check if the user exists in the database
    user_in_db = db_controller.find_document(
        "JagCoaching", 
        "users", 
        {"email": user['username']}
    )

    # If user doesn't exist, return error
    if not user_in_db:
        return {"status": "error", "message": "User not found"}

    # TODO: Verify password here (you'd need to hash passwords in your actual implementation)
    # This is just a placeholder for basic functionality
    print(user)
    return {"status": "success", "message": "Login successful!"}

@router.post("/register/")
async def register(form: User):
    # Logic for user registration
    # Initialize the database controller
    print(router.route())
    db_controller = await CloudDBController()
    
    print(db_controller.get_database("JagCoaching"))
    # Check if user already exists
    existing_user = await db_controller.find_document(
        "JagCoaching",
        "users",
        {"email": form.email}
    )

    # If user already exists, return error
    if existing_user:
        return {"status": "error", "message": "User with this email already exists"}

    # Create new user document
    user_document = {
        "email": form.email,
        "username": form.username,
        "created_at": datetime.now(),
        "last_login": None
    }
        # "password": form.password,  # TODO: Hash the password

    # Add user to the database
    result = db_controller.add_document("JagCoaching", "users", user_document)

    # Check if user was successfully added
    if not result.acknowledged:
        return {"status": "error", "message": "Failed to create user"}
    print(user)
    return {"status": "success", "message": "Registration successful!"}
    
# Logout endpoint
@router.post("/api/logout/")
async def logout(current_user: User = Depends(get_current_user)):
    print(current_user)
    return {"status": "success", "message": "Logout successful!"}


@router.get("/me/")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"status": "success", "user": current_user}



# # Old Routes before routing to routers


# # Login endpoint
# @app.post("/api/login/")
# def login(form: User):
#     print(form)

#     return {"status": "success", "message": "Login successful! test"}

# # Logout endpoint
# @app.post("/api/logout/")
# def logout(form: User):
#     print(form)
#     return {"status": "success", "message": "Logout successful!"}

# # Signup endpoint
# @app.post("/api/register/")
# # def register(username: str, email: str, password: str):
# def register(form: User):
#     username = form.username
#     email = form.email
#     password = form.password
#     print(username, email, password)
#     return {"status": "success", "message": "Registration successful!", "user": {"username": username, "email": email}}


# # Check if the user is logged in
# @app.get("/api/user/")
# def get_user_info(username: str = Depends(login)):
#     if not username:
#         return {"status": "error", "message": "User not found!"}
#     else:
#         return {"status": "success", "message": "User found!", "username": username}
