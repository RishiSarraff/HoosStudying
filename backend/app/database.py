from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()

Base = declarative_base()

# Lazy initialization - these will be set on first use
_connector = None
_engine = None
_localSession = None

def _get_connector():
    global _connector
    if _connector is None:
        _connector = Connector()
    return _connector

def _get_engine():
    global _engine
    if _engine is None:
        instance_password = os.getenv("INSTANCE_PASSWORD")
        db_name = os.getenv("DATABASE_NAME")
        instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
        db_user = os.getenv("DB_USER")
        echoVal = os.getenv("ENVIRONMENT", "development") == "development"
        
        def getconn():
            conn = _get_connector().connect(
                instance_connection_name,  
                "pymysql",
                user=db_user,
                password=instance_password,
                db=db_name
            )
            return conn
        
        _engine = create_engine(
            "mysql+pymysql://",
            creator=getconn,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=echoVal
        )
    return _engine

def _get_session_maker():
    global _localSession
    if _localSession is None:
        _localSession = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _localSession

def get_db():
    db = _get_session_maker()()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()