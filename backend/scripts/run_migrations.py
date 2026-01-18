"""
Database migration runner for ResolveAI
Executes SQL migrations against Supabase PostgreSQL
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    return create_client(url, key)

def run_migration(client: Client, migration_file: Path) -> None:
    """Execute a single migration file"""
    print(f"Running migration: {migration_file.name}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    for i, statement in enumerate(statements, 1):
        try:
            # Use Supabase RPC to execute raw SQL
            client.rpc('exec_sql', {'sql_query': statement}).execute()
            print(f"  ✓ Executed statement {i}/{len(statements)}")
        except Exception as e:
            print(f"  ✗ Error in statement {i}: {e}")
            raise

def main():
    """Run all pending migrations"""
    print("=" * 60)
    print("ResolveAI Database Migration Runner")
    print("=" * 60)
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent.parent / "app" / "db" / "migrations"
    
    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found: {migrations_dir}")
        return
    
    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("No migration files found")
        return
    
    print(f"Found {len(migration_files)} migration files\n")
    
    # Initialize Supabase client
    try:
        client = get_supabase_client()
        print("✓ Connected to Supabase\n")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        return
    
    # Run each migration
    for migration_file in migration_files:
        try:
            run_migration(client, migration_file)
            print(f"✓ Migration {migration_file.name} completed\n")
        except Exception as e:
            print(f"✗ Migration {migration_file.name} failed: {e}")
            print("\nStopping migration process")
            return
    
    print("=" * 60)
    print("✓ All migrations completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
