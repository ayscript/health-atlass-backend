import os
from fastapi import Header, HTTPException, Depends
from supabase import Client
from typing import Annotated, Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = Client.create(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_ANON_KEY)

async def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
):
    """
    Dependency function to verify the user's Supabase access token.
    
    Args:
        supabase: The Supabase client instance.
        authorization: The Authorization header (e.g., "Bearer <token>").

    Returns:
        The authenticated Supabase user object (dict or object based on client version).
    
    Raises:
        HTTPException: 401 Unauthorized if the token is missing or invalid.
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing or invalid format (Expected 'Bearer <token>')"
        )

    # 1. Extract the JWT token
    token = authorization.split(" ")[1]

    try:
        # 2. Verify the token using the Supabase client
        # The user() method verifies the JWT and returns the user object if valid.
        response = supabase.auth.get_user(token)

        # The actual user object is usually in a 'user' attribute on the response
        if not response or not response.user:
             raise HTTPException(status_code=401, detail="Invalid or expired token")

        # 3. Return the authenticated user object
        # Note: The response.user object structure depends on the supabase-py version
        return response.user
        
    except Exception as e:
        # This catches errors during token validation (e.g., JWT decode failure)
        # print(f"Token validation error: {e}") 
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Define an alias for easier route usage
CurrentUser = Annotated[dict, Depends(get_current_user)]