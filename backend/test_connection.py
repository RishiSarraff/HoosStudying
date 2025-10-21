from app.database import engine, db_name
from sqlalchemy.sql import text

try:
    with engine.connect() as connection:
        print("Database connection successful")
        print("Connected to database: ", db_name)

        result = connection.execute(text("SELECT 1"))
        current_db = result.fetchone()[0]
        print("Current DB selected: ", current_db)
except Exception as e:
    print("Database connection failed")
    print("Error: ", str(e))