"""
Supabase service wrapper for database operations with connection pooling and CRUD helpers.
"""
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from postgrest.base_request_builder import APIResponse
from app.config import settings
from app.core.errors import DatabaseError, SupabaseError

async def init_supabase():
    """Initialize Supabase client on application startup."""
    # Force initialization of the singleton
    SupabaseService.get_client()
    print("[Supabase] Client initialized")



class SupabaseService:
    """Singleton wrapper for Supabase client with enhanced query helpers."""
    
    _instance: Client | None = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance
    
    @classmethod
    async def select(
        cls,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Select rows from a table with optional filters.
        
        Args:
            table: Table name
            columns: Columns to select (default: all)
            filters: Dict of column:value filters
            order_by: Column to order by
            limit: Maximum rows to return
        
        Returns:
            List of matching rows
        
        Raises:
            SupabaseError: If query fails
        """
        try:
            client = cls.get_client()
            query = client.table(table).select(columns)
            
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            
            if order_by:
                query = query.order(order_by)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            return response.data or []
        
        except Exception as e:
            raise SupabaseError(
                message=f"Failed to select from {table}",
                details={"table": table, "error": str(e)}
            )
    
    @classmethod
    async def insert(
        cls,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a row into a table.
        
        Args:
            table: Table name
            data: Row data to insert
        
        Returns:
            Inserted row with generated fields
        
        Raises:
            SupabaseError: If insert fails
        """
        try:
            client = cls.get_client()
            response = client.table(table).insert(data).execute()
            
            if not response.data:
                raise SupabaseError(
                    message=f"Insert to {table} returned no data",
                    details={"table": table}
                )
            
            return dict(response.data[0])
        
        except Exception as e:
            raise SupabaseError(
                message=f"Failed to insert into {table}",
                details={"table": table, "error": str(e)}
            )
    
    @classmethod
    async def update(
        cls,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            filters: Dict of column:value filters for WHERE clause
            data: Data to update
        
        Returns:
            Updated rows
        
        Raises:
            SupabaseError: If update fails
        """
        try:
            client = cls.get_client()
            query = client.table(table).update(data)
            
            for column, value in filters.items():
                query = query.eq(column, value)
            
            response = query.execute()
            return response.data or []
        
        except Exception as e:
            raise SupabaseError(
                message=f"Failed to update {table}",
                details={"table": table, "error": str(e)}
            )
    
    @classmethod
    async def delete(
        cls,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Delete rows from a table.
        
        Args:
            table: Table name
            filters: Dict of column:value filters for WHERE clause
        
        Returns:
            Deleted rows
        
        Raises:
            SupabaseError: If delete fails
        """
        try:
            client = cls.get_client()
            query = client.table(table).delete()
            
            for column, value in filters.items():
                query = query.eq(column, value)
            
            response = query.execute()
            return response.data or []
        
        except Exception as e:
            raise SupabaseError(
                message=f"Failed to delete from {table}",
                details={"table": table, "error": str(e)}
            )
    
    @classmethod
    async def get_by_id(
        cls,
        table: str,
        id_value: str,
        id_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single row by ID.
        
        Args:
            table: Table name
            id_value: ID value
            id_column: ID column name (default: "id")
        
        Returns:
            Row data or None if not found
        """
        rows = await cls.select(table, filters={id_column: id_value})
        return rows[0] if rows else None


# Convenience function
def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return SupabaseService.get_client()

