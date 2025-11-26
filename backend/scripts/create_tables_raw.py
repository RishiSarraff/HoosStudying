from sqlalchemy import text
from app.database import engine
from app.schemas import ALL_TABLES

def create_all_tables():
    with engine.connect() as connection:
        for i, create_statement in enumerate(ALL_TABLES, 1):
            try:
                print(f"Executing table creation {i}/{len(ALL_TABLES)}...")
                connection.execute(text(create_statement))
                connection.commit()
                print(f"Table {i} created successfully")
            except Exception as e:
                print(f"Error creating table {i}: {e}")
                connection.rollback()
if __name__ == "__main__":
    create_all_tables()