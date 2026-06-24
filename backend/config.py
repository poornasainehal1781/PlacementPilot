import os
import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_resume_analyzer_12938")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_key_resume_analyzer_98231")
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=30)
    
    # Database URL configuration
    # Try to read DATABASE_URL, default to MySQL local, fallback logic is implemented in database.py
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/ai_resume_analyzer")
    
    # Upload parameters
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
