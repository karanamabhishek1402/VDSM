"""
Database service for Supabase operations.
"""
from supabase import create_client, Client
from config import get_settings

settings = get_settings()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_user_by_email(email: str):
    """
    Retrieve a user from the database by their email.
    """
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

def get_user_by_id(user_id: str):
    """
    Retrieve a user from the database by their ID.
    """
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

def get_user_by_username(username: str):
    """
    Retrieve a user from the database by their username.
    """
    response = supabase.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None

def create_new_user(email: str, username: str, hashed_password: str, full_name: str):
    """
    Create a new user in the database.
    """
    user_data = {
        "email": email,
        "username": username,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "is_active": True,
        "is_verified": False
    }
    response = supabase.table("users").insert(user_data).execute()
    return response.data[0] if response.data else None

def user_exists_by_email(email: str) -> bool:
    """
    Check if a user with the given email exists.
    """
    user = get_user_by_email(email)
    return user is not None

def user_exists_by_username(username: str) -> bool:
    """
    Check if a user with the given username exists.
    """
    user = get_user_by_username(username)
    return user is not None
