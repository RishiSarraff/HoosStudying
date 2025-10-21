from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

project_name = os.getenv("PROJECT_NAME")
instance_id = os.getenv("INSTANCE_ID")
instance_password = os.getenv("INSTANCE_PASSWORD")
db_name = os.getenv("DATABASE_NAME")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
host = os.getenv("HOST")
port = os.getenv("PORT")
db_user = os.getenv("DB_USER")

echoVal = os.getenv("ENVIRONMENT", "development") == "development"

connection_string = f"mysql+pymysql://{db_user}:{instance_password}@{host}:{port}/{db_name}"

engine = create_engine(
    connection_string,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=echoVal  #Turns into false when we change ENVIRONMENT in env to production when deploying
)

# Create a Session Factory
localSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to manage a DB Session for FastAPI Routes
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()
