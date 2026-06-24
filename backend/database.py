import os
import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    resumes = db.relationship('Resume', backref='user', lazy=True, cascade="all, delete-orphan")
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=True)        # JSON string of list of skills
    experience = db.Column(db.Text, nullable=True)    # JSON string of parsed experience details
    education = db.Column(db.Text, nullable=True)     # JSON string of parsed education details
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    analyses = db.relationship('Analysis', backref='resume', lazy=True, cascade="all, delete-orphan")

    def set_skills(self, skills_list):
        self.skills = json.dumps(skills_list)

    def get_skills(self):
        return json.loads(self.skills) if self.skills else []

    def set_experience(self, exp_data):
        self.experience = json.dumps(exp_data)

    def get_experience(self):
        return json.loads(self.experience) if self.experience else []

    def set_education(self, edu_data):
        self.education = json.dumps(edu_data)

    def get_education(self):
        return json.loads(self.education) if self.education else []

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "skills": self.get_skills(),
            "experience": self.get_experience(),
            "education": self.get_education(),
            "created_at": self.created_at.isoformat()
        }

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(db.Text, nullable=True)  # JSON string of list of skills
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    analyses = db.relationship('Analysis', backref='job_description', lazy=True, cascade="all, delete-orphan")

    def set_skills(self, skills_list):
        self.skills_required = json.dumps(skills_list)

    def get_skills(self):
        return json.loads(self.skills_required) if self.skills_required else []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "skills_required": self.get_skills(),
            "created_at": self.created_at.isoformat()
        }

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    ats_score = db.Column(db.Float, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    missing_skills = db.Column(db.Text, nullable=True)   # JSON string of missing skills
    recommendations = db.Column(db.Text, nullable=True)  # JSON string of markdown recommendations
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    questions = db.relationship('InterviewQuestion', backref='analysis', lazy=True, cascade="all, delete-orphan")

    def set_missing_skills(self, skills_list):
        self.missing_skills = json.dumps(skills_list)

    def get_missing_skills(self):
        return json.loads(self.missing_skills) if self.missing_skills else []

    def set_recommendations(self, recs):
        self.recommendations = json.dumps(recs)

    def get_recommendations(self):
        return json.loads(self.recommendations) if self.recommendations else {}

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "ats_score": self.ats_score,
            "similarity_score": self.similarity_score,
            "missing_skills": self.get_missing_skills(),
            "recommendations": self.get_recommendations(),
            "created_at": self.created_at.isoformat()
        }

class InterviewQuestion(db.Model):
    __tablename__ = 'interview_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer_guideline = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False) # 'technical' or 'behavioral'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "question": self.question,
            "answer_guideline": self.answer_guideline,
            "question_type": self.question_type,
            "created_at": self.created_at.isoformat()
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    current_question_index = db.Column(db.Integer, default=0, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_id": self.analysis_id,
            "current_question_index": self.current_question_index,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat()
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False) # 'interviewer' or 'student'
    message = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text, nullable=True) # JSON string of evaluation
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_feedback(self, feedback_data):
        self.feedback = json.dumps(feedback_data) if feedback_data else None

    def get_feedback(self):
        return json.loads(self.feedback) if self.feedback else None

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "sender": self.sender,
            "message": self.message,
            "feedback": self.get_feedback(),
            "created_at": self.created_at.isoformat()
        }


def init_db_fallback(app):
    """
    Initializes the database with fallback logic:
    1. Try to connect to MySQL database configured in DATABASE_URL.
    2. If connection fails or database does not exist, automatically attempt to create the database.
    3. If MySQL completely fails to connect, fallback to SQLite.
    """
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    # If the configured URL is MySQL, try to verify connection
    if db_uri.startswith("mysql"):
        try:
            # Parse database name from URI
            # Example: mysql+pymysql://root:password@localhost:3306/db_name
            base_uri, db_name = db_uri.rsplit('/', 1)
            # Add database creation options if we need to create it
            temp_engine = create_engine(base_uri)
            with temp_engine.connect() as conn:
                # Try to create database if it doesn't exist
                conn.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"[Database] Successfully verified/created MySQL database: {db_name}")
        except Exception as e:
            print(f"[Database] Warning: MySQL connection failed with error: {e}")
            print("[Database] Falling back to SQLite database.")
            # Set SQLAlchemy URI to SQLite
            db_path = os.path.join(app.root_path, "resume_analyzer.db")
            db_uri = f"sqlite:///{db_path}"
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
            
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print(f"[Database] Database tables initialized successfully on: {app.config['SQLALCHEMY_DATABASE_URI']}")
