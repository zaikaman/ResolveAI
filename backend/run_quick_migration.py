"""
Quick migration script to add is_paid_off and paid_off_at columns to debts table
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    # Connect to Supabase
    client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    print("✓ Connected to Supabase")
    
    # Read migration file
    with open('app/db/migrations/004_add_debt_paid_off.sql', 'r') as f:
        sql = f.read()
    
    print("\nExecuting migration...")
    print(sql)
    
    # Execute using PostgREST SQL function if available, or manual approach
    # Note: Supabase doesn't expose direct SQL execution via client library
    # This needs to be run in Supabase SQL Editor
    print("\n⚠️  Please run this SQL in your Supabase SQL Editor:")
    print("-" * 60)
    print(sql)
    print("-" * 60)

if __name__ == "__main__":
    main()
