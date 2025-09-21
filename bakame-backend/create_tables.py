from app.models.database import create_tables

if __name__ == "__main__":
    try:
        create_tables()
        print("✅ Tables created successfully in Supabase!")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
