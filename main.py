from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pydantic import BaseModel, EmailStr
from supabase import Client

from dependency import get_current_user

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = Client.create(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_ANON_KEY)

app = FastAPI(title="Health Atlas AI API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to fast api"}


class UserSignup(BaseModel):
    """Schema for the user signup request body."""

    email: EmailStr  # Requires a valid email address format
    password: str  # The user's chosen password
    display_name: str


@app.post("/auth/signup")
def signup(user: UserSignup):
    """
    Handles user signup with email, password, and display name.
    """
    try:
        # 1. Access the data from the request body
        email = user.email
        password = user.password
        display_name = user.display_name

        # 2. Call the sign-up method on supabase
        supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": os.getenv("SIGNUP_REDIRECT_URL"),
                    "data": {"display_name": display_name},
                },
            }
        )

        # successful registration response
        return {
            "message": "User signed up successfully",
            "email": email,
            "display_name": display_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        # Handle exceptions during the signup process (e.g., email already exists)
        # print(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=f"Signup failed: {e}")


class UserLogin(BaseModel):
    """Schema for the user login request body."""

    email: EmailStr  # Requires a valid email address format
    password: str  # The user's password


@app.post("/auth/login")
def login(user: UserLogin):
    """ "Handles user's login with email and password"""

    try:
        email = user.email
        password = user.password

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        # print(response.session.user.user_metadata)

        return {
            "message": "login successfully",
            "auth_token": response.session.access_token,
            "user": response.session.user.user_metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        # Handle exceptions during the signup process (e.g., email already exists)
        # print(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=f"Login failed: {e}")


class UserForgotPassword(BaseModel):
    """Schema for the user forgot password body."""

    email: EmailStr  # Requires a valid email address format


@app.post("/auth/forgot-password")
def forgot_password(user: UserForgotPassword):

    try:
        email = user.email
        supabase.auth.reset_password_email(email)

        return {"message": f"password reset email sent to {email}"}

    except HTTPException:
        raise
    except Exception as e:
        # Handle exceptions during the signup process (e.g., email already exists)
        # print(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=f"Password reset failed: {e}")


@app.get("/api/profile")
async def read_user_profile(user: dict = Depends(get_current_user)):
    """
    This route requires a valid Supabase access token.
    If authentication succeeds, 'user' will contain the user data.
    """

    try:
        # Check for metadata
        user_metadata = getattr(user, "user_metadata", {})
        display_name = user_metadata.get("display_name", "No Display Name Set")

        return {
            "message": "user retrieved successfully!",
            "user": {
                "user_id": user.id,
                "email": user.email,
                "display_name": display_name,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User retrieval failed: {e}")
