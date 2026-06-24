import sys
import os
import unittest

# Ensure the root folder is in the search path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.parser import extract_email, extract_phone, extract_skills, extract_name
from backend.analyzer import calculate_similarity, analyze_resume_against_job
from backend.questions import generate_questions
from backend.app import create_app
from backend.database import db, User, Resume, JobDescription, Analysis

class TestBackendLogic(unittest.TestCase):
    
    def setUp(self):
        # Sample resume text
        self.resume_text = """
        John Doe
        Email: john.doe@example.com
        Phone: (123) 456-7890
        
        Professional Experience:
        Senior Software Engineer - TechCorp (2020 - Present)
        Developed full-stack web applications using Python, Flask, and React.
        Designed database schemas in MySQL and PostgreSQL.
        Managed containerized microservices deployment using Docker and AWS.
        
        Education:
        B.S. in Computer Science - University of State (2016-2020)
        """
        
        # Sample job description text
        self.job_description = """
        Position: Senior Python Developer
        We are seeking a Software Engineer with experience in Python, Flask, and Docker.
        You should have SQL experience (MySQL preferred).
        Experience with Kubernetes and Machine Learning is a plus.
        """

    def test_parser_regex(self):
        # Email parsing
        email = extract_email(self.resume_text)
        self.assertEqual(email, "john.doe@example.com")
        
        # Phone parsing
        phone = extract_phone(self.resume_text)
        self.assertIsNotNone(phone)
        self.assertTrue("123" in phone)
        
        # Name parsing
        name = extract_name(self.resume_text)
        self.assertEqual(name, "John Doe")

    def test_parser_skills(self):
        # Skills extraction
        skills = extract_skills(self.resume_text)
        self.assertIn("Python", skills)
        self.assertIn("Flask", skills)
        self.assertIn("React", skills)
        self.assertIn("MySQL", skills)
        self.assertIn("Docker", skills)

    def test_similarity_scoring(self):
        # Cosine similarity
        score = calculate_similarity("Python React developer", "Seeking Python and React developer")
        self.assertGreater(score, 0.0)
        
        # Complete Analysis
        resume_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(123) 456-7890",
            "skills": ["Python", "Flask", "React", "MySQL", "Docker"],
            "experience": ["Senior Software Engineer at TechCorp"],
            "education": ["BS in Computer Science"],
            "raw_text": self.resume_text
        }
        
        analysis = analyze_resume_against_job(resume_data, "Senior Python Developer", self.job_description)
        
        self.assertGreater(analysis["ats_score"], 40.0) # Should be high because it matches multiple skills
        self.assertIn("Python", analysis["matched_skills"])
        self.assertIn("Kubernetes", analysis["missing_skills"])

    def test_question_generation(self):
        resume_skills = ["Python", "React", "Docker"]
        missing_skills = ["Kubernetes", "Machine Learning"]
        
        questions = generate_questions(resume_skills, missing_skills)
        
        self.assertGreater(len(questions), 0)
        # Should include behavioral questions
        self.assertTrue(any("Behavioral" in q["question_type"] for q in questions))

    def test_custom_resume_questions(self):
        resume_skills = ["Python", "React"]
        missing_skills = []
        resume_data = {
            "raw_text": """
            Jane Developer
            jane@example.com
            
            Experience:
            Senior Engineer at Google
            - Reduced API latency by 45% in core endpoints.
            - Configured Redis caching for distributed sessions.
            - Mentored 4 junior software engineers on clean architecture.
            """,
            "experience": ["Senior Engineer at Google", "Reduced API latency by 45% in core endpoints.", "Configured Redis caching for distributed sessions.", "Mentored 4 junior software engineers on clean architecture."],
            "skills": ["Python", "React"]
        }
        
        questions = generate_questions(resume_skills, missing_skills, resume_data)
        
        # Verify that questions contain our achievements and leadership custom text
        question_texts = [q["question"] for q in questions]
        question_types = [q["question_type"] for q in questions]
        
        # 1. Custom achievement question should be generated
        self.assertTrue(any("Reduced API latency by 45%" in q for q in question_texts))
        self.assertIn("Technical (Achievement)", question_types)
        
        # 2. Custom tool/infrastructure question should be generated
        self.assertTrue(any("Redis" in q or "REDIS" in q.upper() for q in question_texts))
        self.assertIn("Technical (Architecture)", question_types)
        
        # 3. Custom leadership question should be generated
        self.assertTrue(any("Mentored 4 junior software engineers" in q for q in question_texts))
        self.assertIn("Behavioral (Leadership)", question_types)


    def test_database_creation(self):
        # Create a Flask app configured with an in-memory SQLite database
        app = create_app({
            'SQLALCHEMY_DATABASE_URI': "sqlite:///:memory:",
            'TESTING': True
        })
        
        with app.app_context():
            # Verify tables can be created
            db.create_all()
            
            # 1. Test User registration
            user = User(username="tester", email="test@example.com")
            user.set_password("securepassword")
            db.session.add(user)
            db.session.commit()
            
            # Verify user fields
            queried_user = User.query.filter_by(username="tester").first()
            self.assertIsNotNone(queried_user)
            self.assertTrue(queried_user.check_password("securepassword"))
            
            # 2. Test Resume insertion
            resume = Resume(user_id=queried_user.id, filename="resume.pdf", raw_text="Developer resume content")
            resume.set_skills(["Python", "React"])
            db.session.add(resume)
            db.session.commit()
            
            self.assertIn("Python", resume.get_skills())

if __name__ == '__main__':
    unittest.main()
