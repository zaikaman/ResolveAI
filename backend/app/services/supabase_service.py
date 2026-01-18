"""
Supabase service wrapper for database operations
"""
from supabase import create_client, Client
from app.config import settings


class SupabaseService:
    """Singleton wrapper for Supabase client"""
    
    _instance: Client | None = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance


# Convenience function
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return SupabaseService.get_client()
