"""
Database service for Supabase operations.
"""
from supabase import create_client, Client
from config import get_settings
from typing import List, Dict, Any, Optional
import json

settings = get_settings()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

class DBService:
    """Database service wrapper"""
    
    def __init__(self):
        self.client = supabase
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query via Supabase.
        Note: For production use, implement proper RPC functions in Supabase
        """
        try:
            # Use Supabase's postgrest client for raw queries
            response = self.client.rpc('execute_sql', {
                'query': query,
                'params': json.dumps(params) if params else '{}'
            }).execute()
            
            return response.data if response.data else []
        except Exception as e:
            # For this implementation, we'll use table API methods instead
            raise NotImplementedError(
                f"Raw SQL execution not available. Use table API methods. Error: {e}"
            )
    
    def get_user_by_email(self, email: str):
        """Retrieve a user by email"""
        response = self.client.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_id(self, user_id: str):
        """Retrieve a user by ID"""
        response = self.client.table("users").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_username(self, username: str):
        """Retrieve a user by username"""
        response = self.client.table("users").select("*").eq("username", username).execute()
        return response.data[0] if response.data else None
    
    def create_new_user(self, email: str, username: str, hashed_password: str, full_name: str):
        """Create a new user"""
        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_verified": False
        }
        response = self.client.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    
    def user_exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        user = self.get_user_by_email(email)
        return user is not None
    
    def user_exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        user = self.get_user_by_username(username)
        return user is not None


# Global instance
db_service = DBService()

# Legacy function exports for backward compatibility
def get_user_by_email(email: str):
    return db_service.get_user_by_email(email)

def get_user_by_id(user_id: str):
    return db_service.get_user_by_id(user_id)

def get_user_by_username(username: str):
    return db_service.get_user_by_username(username)

def create_new_user(email: str, username: str, hashed_password: str, full_name: str):
    return db_service.create_new_user(email, username, hashed_password, full_name)

def user_exists_by_email(email: str) -> bool:
    return db_service.user_exists_by_email(email)

def user_exists_by_username(username: str) -> bool:
    return db_service.user_exists_by_username(username)
