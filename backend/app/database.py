from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()

project_name = os.getenv("PROJECT_NAME")
instance_id = os.getenv("INSTANCE_ID")
instance_password = os.getenv("INSTANCE_PASSWORD")
db_name = os.getenv("DATABASE_NAME")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
db_user = os.getenv("DB_USER")

echoVal = os.getenv("ENVIRONMENT", "development") == "development"

connector = Connector()

def getconn():
    conn = connector.connect(
        instance_connection_name,  
        "pymysql",
        user=db_user,
        password=instance_password,
        db=db_name
    )
    return conn

engine = create_engine(
    "mysql+pymysql://",
    creator=getconn,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=echoVal
)

localSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = localSession()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()