import unittest
import os
import sys

# Ensure the root folder is in the search path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.deep_questions import generate_deep_questions

class TestDeepQuestions(unittest.TestCase):
    def setUp(self):
        self.resume_data = {
            "name": "Jane Developer",
            "email": "jane@example.com",
            "phone": "555-0199",
            "skills": ["Python", "Flask", "React", "MySQL", "NLP", "Docker"],
            "experience": [
                "Software Engineer Intern - TechSolutions (2023 - 2024)",
                "Developed scalable full-stack placement portals using React and Python/Flask.",
                "Optimized database indexing in MySQL to speed up search response time by 40%."
            ],
            "education": ["BS in Computer Science"],
            "raw_text": """
            Jane Developer
            jane@example.com | 555-0199
            
            Technical Skills:
            Python, Flask, React, MySQL, NLP, Docker, AWS
            
            Experience:
            Software Engineer Intern at TechSolutions (2023 - 2024)
            - Built an interactive full-stack placement portal using React and Flask backend.
            - Designed database schemas in MySQL and PostgreSQL.
            - Optimized query indexing to reduce latency.
            
            Projects:
            AI Placement Mentor Web App
            - Implemented resume parsing and ATS scoring logic.
            - Developed AI-based interview question generation.
            """
        }
        self.job_title = "Full-Stack Software Engineer"
        self.job_description = "We are seeking a developer skilled in Python, Flask, React, and SQL database storage. Experience with Docker and AWS is preferred."

    def test_offline_question_generation(self):
        # Explicitly remove environment keys to force offline generation
        original_gemini_key = os.environ.get("GEMINI_API_KEY")
        original_google_key = os.environ.get("GOOGLE_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]

        try:
            result = generate_deep_questions(self.resume_data, self.job_title, self.job_description)
            
            # Check structure
            self.assertIn("resume_summary", result)
            self.assertIn("questions", result)
            
            summary = result["resume_summary"]
            self.assertIn("key_skills", summary)
            self.assertIn("projects", summary)
            self.assertIn("internship_highlights", summary)
            self.assertIn("strong_claims", summary)
            
            # Verify details
            self.assertGreater(len(summary["key_skills"]), 0)
            self.assertGreater(len(summary["projects"]), 0)
            
            questions = result["questions"]
            self.assertGreater(len(questions), 0)
            
            # Check if questions have correct keys
            for q in questions:
                self.assertIn("question", q)
                self.assertIn("answer_guideline", q)
                self.assertIn("question_type", q)
                self.assertTrue(isinstance(q["question"], str))
                self.assertTrue(isinstance(q["answer_guideline"], str))
                self.assertTrue(isinstance(q["question_type"], str))
                
                # Guidelines should contain Key Talking Points
                self.assertIn("**Key Talking Points to Include:**", q["answer_guideline"])
                
            # Verify specific question categories were generated
            proj_qs = [q for q in questions if "Project:" in q["question_type"]]
            self.assertGreater(len(proj_qs), 0)
            
            claim_qs = [q for q in questions if "Claim Verification" in q["question_type"]]
            self.assertGreater(len(claim_qs), 0)

        finally:
            # Restore environment keys
            if original_gemini_key is not None:
                os.environ["GEMINI_API_KEY"] = original_gemini_key
            if original_google_key is not None:
                os.environ["GOOGLE_API_KEY"] = original_google_key

if __name__ == "__main__":
    unittest.main()
