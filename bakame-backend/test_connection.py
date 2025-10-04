from app.models.database import engine

try:
    connection = engine.connect()
    print("✅ Connected to Supabase successfully!")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
