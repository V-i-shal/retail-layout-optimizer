"""Configuration module for the retail layout optimizer."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Application configuration from environment variables."""
    
    # MySQL Database Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'retail_optimizer')
    
    # SQLAlchemy Database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL query logging
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Pipeline Configuration
    RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))
    
    # Data Paths
    DATA_DIR = BASE_DIR / 'data'
    SQL_DIR = BASE_DIR / 'sql'
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.MYSQL_PASSWORD:
            raise ValueError("MYSQL_PASSWORD must be set in .env file")
        if not cls.MYSQL_DB:
            raise ValueError("MYSQL_DB must be set in .env file")
        return True


# Validate configuration on import
Config.validate()