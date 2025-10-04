import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

direct_connection_string = "postgresql://postgres:BakameAI1230@db.pttxlvbyvhgvwbakabyc.supabase.co:5432/postgres"

try:
    conn = psycopg2.connect(direct_connection_string)
    cursor = conn.cursor()
    
    project_ref = "pttxlvbyvhgvwbakabyc"
    pooler_password = "BakameAI1230"
    
    create_role_sql = f"""
    do $$
    begin
    if not exists (
        select 1 from pg_roles
        where rolname = 'postgres.{project_ref}'
    ) then
        create role "postgres.{project_ref}"
        with login
        encrypted password '{pooler_password}';
    else
        raise notice 'Role already exists, skipping create.';
    end if;
    end$$;
    """
    
    cursor.execute(create_role_sql)
    
    grant_sql = f"""
    grant connect on database postgres to "postgres.{project_ref}";
    grant usage on schema public to "postgres.{project_ref}";
    grant all privileges on all tables in schema public to "postgres.{project_ref}";
    """
    
    cursor.execute(grant_sql)
    
    md5_sql = f"""
    set password_encryption = 'md5';
    alter role "postgres.{project_ref}" with password '{pooler_password}';
    """
    
    cursor.execute(md5_sql)
    
    conn.commit()
    print("✅ Pooler role created successfully!")
    
except Exception as e:
    print(f"❌ Failed to create pooler role: {e}")
    print("Trying with pooler connection instead...")
    
finally:
    if 'conn' in locals():
        conn.close()
