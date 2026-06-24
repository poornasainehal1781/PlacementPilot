import os
import re
import json
import traceback
from backend.parser import get_nlp
from backend.questions import extract_projects_from_text, extract_custom_resume_bullets

def generate_deep_questions(resume_data, job_title, job_description):
    """
    Generates deep, project-specific, and technology-specific interview questions 
    based on the candidate's resume and target job requirements.
    
    Tries to use Gemini API first, falling back to a robust offline generator if not configured or fails.
    """
    # Try using Gemini API
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            return generate_questions_via_gemini(resume_data, job_title, job_description, api_key)
        except Exception as e:
            print(f"[DeepQuestions] Gemini generation failed: {e}")
            traceback.print_exc()
            print("[DeepQuestions] Falling back to offline question generator...")
            
    # Fallback to offline rule-based generator
    return generate_questions_offline(resume_data, job_title, job_description)

def generate_questions_via_gemini(resume_data, job_title, job_description, api_key):
    """
    Calls the Gemini API to analyze the resume and job requirements and output structured JSON.
    """
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentConfig

    genai.configure(api_key=api_key)
    
    # Define response JSON schema to guarantee correct format
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "resume_summary": {
                "type": "OBJECT",
                "properties": {
                    "key_skills": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "projects": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "technologies": {
                                    "type": "ARRAY",
                                    "items": {"type": "STRING"}
                                },
                                "description": {"type": "STRING"}
                            },
                            "required": ["title", "technologies"]
                        }
                    },
                    "internship_highlights": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "strong_claims": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": ["key_skills", "projects", "internship_highlights", "strong_claims"]
            },
            "questions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING"},
                        "answer_guideline": {"type": "STRING"},
                        "question_type": {"type": "STRING"}
                    },
                    "required": ["question", "answer_guideline", "question_type"]
                }
            }
        },
        "required": ["resume_summary", "questions"]
    }
    
    # Prepare details
    resume_skills = resume_data.get("skills", [])
    resume_experience = resume_data.get("experience", [])
    resume_education = resume_data.get("education", [])
    resume_text = resume_data.get("raw_text", "")
    
    system_prompt = (
        "You are a senior technical interviewer and AI placement mentor. Your task is to analyze the candidate's "
        "resume and job description to create deep, personalized, project-specific, and technology-focused "
        "interview preparation materials. You must be realistic, and avoid generic theory questions "
        "(e.g., do not ask 'What is React?' or 'What is Flask?'). Instead, ask implementation-focused "
        "questions based on the actual projects and claims in the resume.\n\n"
        "Analyze the resume for:\n"
        "1. Technical skills & frameworks.\n"
        "2. Projects mentioned (title, tech used, features, action verbs).\n"
        "3. Internship and work experiences.\n"
        "4. Strong claims and ownership signals (e.g., 'built', 'implemented', 'optimized', 'designed').\n\n"
        "You must generate questions in multiple categories with 3 difficulty levels:\n"
        "- Category A (Project Understanding): problem solved, end-to-end workflow, architectural choice.\n"
        "- Category B (Technology-Specific): connection of skills (e.g., React, Flask, MySQL, NLP, etc.) to the project.\n"
        "- Category C (Ownership & Implementation): hardest challenges, debugging, backend routes, personal contribution.\n"
        "- Category D (Scenario-Based): scaling for 10k users, performance optimizations, failure scenarios.\n"
        "- Category E (Resume Claim Verification): verification questions for strong claims.\n\n"
        "Set the `question_type` of each generated question to a formatted string containing the mapped project "
        "or experience, the difficulty level, and the category (e.g., 'Project: E-Commerce | Level 2 Intermediate | Technology-Specific' "
        "or 'Claim Verification | Level 3 Deep').\n\n"
        "For each question, the `answer_guideline` MUST contain a paragraph of response strategy guidelines followed by "
        "a clean markdown section: '**Key Talking Points to Include:**\\n- Point 1\\n- Point 2\\n- Point 3' (with 3 to 6 bullet points detailing specific technical words, metrics, or workflows the candidate should discuss).\n"
    )
    
    user_input = f"""
--- TARGET JOB ---
Job Title: {job_title}
Job Description:
{job_description}

--- CANDIDATE RESUME PROFILE ---
Filename: {resume_data.get("filename", "resume.pdf")}
Parsed Skills: {json.dumps(resume_skills)}
Parsed Experience: {json.dumps(resume_experience)}
Parsed Education: {json.dumps(resume_education)}

Raw Resume Text:
{resume_text}
"""
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    config = GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=response_schema,
        temperature=0.2
    )
    
    response = model.generate_content(
        contents=[
            {"role": "user", "parts": [{"text": system_prompt + "\n\n" + user_input}]}
        ],
        config=config
    )
    
    result = json.loads(response.text)
    return result

def extract_projects_clean(raw_text):
    """
    Cleans raw resume text and extracts actual project headers.
    Filters out bullet points, technology stack lists, and lines starting with action verbs.
    """
    import re
    if not raw_text:
        return []
        
    lines = raw_text.split("\n")
    project_keywords = ["projects", "personal projects", "academic projects", "key projects", "key initiatives", "notable projects"]
    
    proj_lines = []
    is_proj_section = False
    
    action_verbs = {
        "developed", "engineered", "implemented", "optimized", "designed", "built", "created", 
        "completed", "processed", "integrated", "applied", "utilized", "analyzed", "collaborated", 
        "spearheaded", "led", "managed", "supervised", "automated", "tested", "deployed"
    }
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_lower = line_clean.lower()
        
        # Check if line marks start of projects section
        if any(pkey in line_lower for pkey in project_keywords) and len(line_clean) < 30:
            is_proj_section = True
            continue
            
        # Check if line marks start of another section
        if is_proj_section and any(ekey in line_lower for ekey in ["experience", "education", "skills", "work history", "certifications", "interests", "languages", "internships"]) and len(line_clean) < 30:
            is_proj_section = False
            break
            
        if is_proj_section:
            # Skip bulleted items
            if line_clean.startswith(("-", "•", "*", "\u2022")):
                continue
                
            # Clean leading bullet symbol if it exists
            line_no_bullet = re.sub(r'^\s*[-•*\u2022]\s*', '', line_clean).strip()
            line_words = line_no_bullet.lower().split()
            
            if not line_words:
                continue
                
            # Skip if the line starts with an action verb
            if line_words[0] in action_verbs:
                continue
                
            # Skip if the line contains multiple pipe separators (usually technology badges list)
            if line_clean.count("|") >= 2 or len(line_clean) < 10:
                continue
                
            # Skip if it's just a general description line fragment
            if any(w in line_lower for w in ["accessibility", "efficiency", "compatibility", "rendering", "multi-language", "usability"]):
                continue
                
            proj_lines.append(line_no_bullet)
            
    # Deduplicate
    seen = set()
    unique_proj = []
    for p in proj_lines:
        if p.lower() not in seen:
            seen.add(p.lower())
            unique_proj.append(p)
            
    return unique_proj

def extract_experience_clean(raw_text):
    """
    Scans the resume for internship or work experience sections.
    Ignores non-work headings and lists relevant responsibility statements.
    """
    if not raw_text:
        return []
        
    lines = raw_text.split("\n")
    exp_keywords = ["experience", "work history", "employment", "internships", "internship", "professional experience"]
    
    exp_list = []
    is_exp_section = False
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_lower = line_clean.lower()
        
        # Check if line marks start of experience/internship section
        if any(ekey in line_lower for ekey in exp_keywords) and len(line_clean) < 30:
            is_exp_section = True
            continue
            
        # Check if line marks start of another section
        if is_exp_section and any(skey in line_lower for skey in ["education", "skills", "projects", "certifications", "interests", "languages"]) and len(line_clean) < 30:
            is_exp_section = False
            break
            
        if is_exp_section:
            if len(line_clean) > 10:
                # Ignore university cities/dates misparsed as experience
                if "warangal" in line_lower or "telangana" in line_lower:
                    continue
                exp_list.append(line_clean)
                
    # Fallback to lines matching 'intern' if no section resolved
    if not exp_list:
        for line in lines:
            line_clean = line.strip()
            if "intern" in line_clean.lower() and len(line_clean) < 100:
                exp_list.append(line_clean)
                
    return exp_list

def generate_questions_offline(resume_data, job_title, job_description):
    """
    Offline rule-based fallback generator. Analyzes skills, projects, and claims 
    using Spacy and regex, and constructs deep questions via template matching.
    """
    raw_text = resume_data.get("raw_text", "")
    resume_skills = resume_data.get("skills", [])
    
    # 1. Extract projects, achievements, and claims
    projects = extract_projects_clean(raw_text)
    custom_bullets = extract_custom_resume_bullets(raw_text)
    achievements = custom_bullets["achievements"]
    leadership = custom_bullets["leadership"]
    advanced_tools = custom_bullets["advanced_tools"]
    
    # Resolve clean internship highlights
    clean_exp = extract_experience_clean(raw_text)
    
    # If no projects found, construct fallback project
    if not projects:
        if clean_exp:
            proj_title = re.sub(r'^\s*[-•*]\s*', '', clean_exp[0]).split("-")[0].strip()
            projects = [proj_title]
        else:
            projects = ["Placement Mentor Web App"]
            
    # Extract claims
    action_verbs = ["built", "implemented", "optimized", "developed", "deployed", "designed", "integrated", "improved", "created"]
    strong_claims = []
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    for line in lines:
        clean_line = re.sub(r'^\s*[-•*\u2022]\s*', '', line).strip()
        if len(clean_line) < 25 or len(clean_line) > 150:
            continue
        line_lower = clean_line.lower()
        if any(f" {verb} " in line_lower or line_lower.startswith(verb) for verb in action_verbs):
            strong_claims.append(clean_line)
            if len(strong_claims) >= 4:
                break
                
    if not strong_claims:
        strong_claims = [
            "Implemented resume parser and extraction algorithm.",
            "Designed and developed full-stack placement portal."
        ]
        
    # Map technologies used in each project by scanning their neighborhood lines in the resume text
    project_tech = {}
    lines_clean = [l.strip() for l in raw_text.split("\n") if l.strip()]
    for proj in projects:
        tech_found = []
        proj_lower = proj.lower()
        
        # Find where the project header occurs in resume text
        proj_idx = -1
        for idx, line in enumerate(lines_clean):
            if proj_lower in line.lower() or line.lower() in proj_lower:
                proj_idx = idx
                break
                
        # Scan lines below it until we hit the next project or a new section
        scan_lines = []
        if proj_idx != -1:
            scan_lines.append(lines_clean[proj_idx])
            for next_idx in range(proj_idx + 1, min(proj_idx + 6, len(lines_clean))):
                next_line = lines_clean[next_idx]
                next_line_lower = next_line.lower()
                
                # Stop if we hit another project title
                is_another_proj = False
                for other_proj in projects:
                    if other_proj != proj and (other_proj.lower() in next_line_lower or next_line_lower in other_proj.lower()):
                        is_another_proj = True
                        break
                if is_another_proj:
                    break
                    
                # Stop if we hit another main section heading
                if any(sec in next_line_lower for sec in ["internships", "experience", "education", "skills", "certifications", "interests", "languages"]) and len(next_line) < 30:
                    break
                    
                scan_lines.append(next_line)
                
        scan_text = " ".join(scan_lines).lower()
            
        # Check standard languages & frameworks
        for skill in ["react", "flask", "mysql", "postgresql", "sqlite", "sql", "python", "nlp", "ai", "ml", "docker", "aws", "html", "css", "javascript", "js", "java", "git"]:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if skill in ["c++", "c#"]:
                pattern = re.escape(skill)
            if re.search(pattern, scan_text):
                display_name = skill.title()
                if skill in ["nlp", "aws", "sql", "html", "css", "js", "ml", "ai"]:
                    display_name = skill.upper()
                if skill == "js":
                    display_name = "JavaScript"
                tech_found.append(display_name)
                
        # Deduplicate
        tech_found = list(dict.fromkeys(tech_found))
        if not tech_found:
            tech_found = ["HTML", "CSS", "JavaScript"]
        project_tech[proj] = tech_found

    # 2. Build Resume Summary Profile data
    resume_summary = {
        "key_skills": resume_skills[:12],
        "projects": [
            {
                "title": proj,
                "technologies": project_tech[proj],
                "description": f"Personal / Academic project leveraging {', '.join(project_tech[proj])}."
            } for proj in projects[:3]
        ],
        "internship_highlights": [
            re.sub(r'^\s*[-•*\u2022]\s*', '', exp) for exp in clean_exp[:3]
        ] if clean_exp else ["Academic training and development projects."],
        "strong_claims": strong_claims[:4]
    }
    
    questions = []
    
    # 3. For each project, generate structured questions
    for proj in projects[:3]:
        techs = project_tech[proj]
        tech_str = ", ".join(techs)
        
        # Category A - Project Understanding (Level 1 Basic)
        questions.append({
            "question": f"What specific problem does the project '{proj}' solve? Can you explain the end-to-end user workflow?",
            "answer_guideline": (
                f"Begin with a clear 1-sentence problem statement. Explain how your application addresses this pain point, "
                f"then trace the workflow step-by-step from input to final output.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- Clear statement of the core problem and user target audience\n"
                f"- The end-to-end data flow (e.g. uploading a PDF -> extraction -> analysis -> dashboard display)\n"
                f"- The main modules that process requests (e.g. parser, analyzer, chatbot)\n"
                f"- The output delivered to the user and how it helps them prepare"
            ),
            "question_type": f"Project: {proj} | Level 1 Basic | Project Understanding"
        })
        
        questions.append({
            "question": f"Why did you choose {tech_str} as the primary stack for '{proj}'? What alternatives did you consider?",
            "answer_guideline": (
                f"Discuss the architectural fit of {tech_str} for this specific project. Contrast it with alternatives "
                f"(such as Flask vs Django, React vs Vanilla JS, or MySQL vs MongoDB) explaining developer speed, scalability, "
                f"or data schema integrity.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- The architectural benefits of your stack (e.g. lightweight backend with Flask, rich SPA features in React)\n"
                f"- Compare database structures (e.g. why SQL was preferred for structured relations or relational integrity)\n"
                f"- Discuss alternative libraries or structures you evaluated\n"
                f"- Performance or setup time constraints that guided the decision"
            ),
            "question_type": f"Project: {proj} | Level 1 Basic | Project Architecture"
        })

        # Category B - Technology-Specific (Level 2 Intermediate)
        # React specific questions
        if any(t.lower() == "react" for t in techs):
            questions.append({
                "question": f"How did you manage components and state in the React frontend of '{proj}'? How does it communicate with the backend?",
                "answer_guideline": (
                    f"Explain component nesting (e.g. upload cards, score display, dashboard panels) and state handling rules. "
                    f"Mention hooks like useState, useEffect, and axios requests with headers.\n\n"
                    f"**Key Talking Points to Include:**\n"
                    f"- Component division: dashboard, analysis audit list, chatbot pane, upload forms\n"
                    f"- State tracking for asynchronous operations (e.g. show loading spinners during parser parsing)\n"
                    f"- React Hooks usage (e.g. useEffect for fetch hooks, useRef for chat scroll alignment)\n"
                    f"- Calling backend endpoints safely (using JWT tokens inside axios headers)"
                ),
                "question_type": f"Project: {proj} | Level 2 Intermediate | Technology-Specific"
            })
            
        # Flask specific questions
        if any(t.lower() == "flask" for t in techs):
            questions.append({
                "question": f"Walk me through the Flask route structure in '{proj}'. How are file uploads, request validation, and database operations handled?",
                "answer_guideline": (
                    f"Explain Flask Blueprints, Flask-SQLAlchemy integration, and route design rules. Walk through file secure saving, "
                    f"JWT auth decoration, and database commit exceptions.\n\n"
                    f"**Key Talking Points to Include:**\n"
                    f"- Blueprint setup: dividing Auth, Resume, Analysis, and Chat routes\n"
                    f"- Safe file upload: checking extensions, file size limits, and sanitizing filename with werkzeug\n"
                    f"- Authentication guards: using @jwt_required() decorators to fetch user ID safely\n"
                    f"- Database lifecycle: opening db sessions, flushing IDs, committing, and handling rollback on exception"
                ),
                "question_type": f"Project: {proj} | Level 2 Intermediate | Technology-Specific"
            })

        # MySQL/SQL specific questions
        if any(t.lower() in ["sql", "mysql", "postgresql", "sqlite"] for t in techs):
            questions.append({
                "question": f"Explain the database schema design of '{proj}'. What tables did you create and how did you enforce referential integrity?",
                "answer_guideline": (
                    f"Explain the tables representing users, resumes, analyses, and interview questions. Mention primary/foreign keys "
                    f"and cascade deletion rules to prevent orphaned rows.\n\n"
                    f"**Key Talking Points to Include:**\n"
                    f"- The exact schema layout (e.g. Users, Resumes, JobDescriptions, Analyses, InterviewQuestions, ChatMessages)\n"
                    f"- Foreign key linkages (e.g. Analysis links to user_id, resume_id, and job_id)\n"
                    f"- Cascade deletes: why deleting a resume automatically deletes related analysis audits and questions\n"
                    f"- Rationale for a relational SQL structure (users-to-resumes 1:N relations, analysis-to-questions 1:N relations)"
                ),
                "question_type": f"Project: {proj} | Level 2 Intermediate | Technology-Specific"
            })

        # NLP/AI/ML specific questions
        if any(t.lower() in ["nlp", "ai", "ml", "generative ai", "streamlit"] for t in techs):
            questions.append({
                "question": f"How is resume parsing or text similarity calculated in '{proj}'? What is rule-based and what is AI-driven?",
                "answer_guideline": (
                    f"Explain text extraction (PyPDF2, python-docx), entity recognition (using SpaCy to extract Person, Email, Phone), "
                    f"and matching algorithms (TF-IDF vectorizer, cosine similarity indices).\n\n"
                    f"**Key Talking Points to Include:**\n"
                    f"- Text parsing extraction layer and handling unstructured layout files\n"
                    f"- Rule-based token matching (regex for emails, phones; dictionary parsing for common skills list)\n"
                    f"- NLP tokenization: using SpaCy models ('en_core_web_sm') for named entity extraction\n"
                    f"- Math logic: TF-IDF vectorization and cosine similarity to rate resume against job description"
                ),
                "question_type": f"Project: {proj} | Level 2 Intermediate | Technology-Specific"
            })

        # HTML/CSS/JavaScript specific questions (for purely frontend projects)
        if any(t.lower() in ["html", "css", "javascript"] for t in techs) and not any(t.lower() in ["react", "flask", "sql", "mysql", "nlp", "ai"] for t in techs):
            questions.append({
                "question": f"How did you structure the HTML, CSS, and JavaScript files in '{proj}'? How did you handle user interactions and page layout?",
                "answer_guideline": (
                    f"Explain the directory structure (e.g. separating assets, scripts, styles). Discuss responsive design using CSS "
                    f"(media queries, flexbox/grid) and dynamic DOM manipulation using Vanilla JavaScript.\n\n"
                    f"**Key Talking Points to Include:**\n"
                    f"- Organizing frontend source code files (HTML template structure, external CSS, module script tags)\n"
                    f"- Responsive styling techniques (flexbox alignment, grid maps, media query breakpoints for mobile/desktop)\n"
                    f"- Dynamic element generation (fetching inputs, updating the DOM with innerHTML/createElement)\n"
                    f"- Client-side interactions (event listener loops, click triggers, validation checks)"
                ),
                "question_type": f"Project: {proj} | Level 2 Intermediate | Technology-Specific"
            })

        # Category C - Ownership & Implementation (Level 2 Intermediate)
        questions.append({
            "question": f"What was the single most difficult technical challenge you personally implemented in '{proj}'? How did you troubleshoot it?",
            "answer_guideline": (
                f"Describe a real engineering roadblock (e.g., PDF text extraction scrambled, database lockups, or similarity score scaling issues). "
                f"Trace your debugging steps, logical analysis, and permanent fix.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- Concrete description of the bug/challenge (e.g. SpaCy missing model error on server startup)\n"
                f"- Investigation steps (e.g. logging backend status, checking subprocess execution, isolating environment)\n"
                f"- The final fix implemented (e.g. wrap loading in try-catch and automatically execute subprocess installation)\n"
                f"- Prevention measures taken to stop regression"
            ),
            "question_type": f"Project: {proj} | Level 2 Intermediate | Ownership & Implementation"
        })

        # Category D - Scenario-Based (Level 3 Deep)
        questions.append({
            "question": f"If '{proj}' suddenly needs to serve 10,000 active students simultaneously, what architectural bottlenecks will emerge? How would you scale it?",
            "answer_guideline": (
                f"Analyze bottlenecks (database connections, slow NLP file parsing, CPU usage). "
                f"Discuss load balancing, task queues (Celery/Redis), read replicas, and frontend static caching.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- Identifying bottleneck nodes: CPU-bound Spacy/TF-IDF processing, SQLite locking under concurrent writes\n"
                f"- Database scaling: transitioning SQLite to PostgreSQL with connection pooling (e.g. pgBouncer)\n"
                f"- Asynchronous execution: using task queues (Celery + Redis) to process resume parsing out-of-band\n"
                f"- Caching: storing common Job Description skill extraction indices in Redis to save computation"
            ),
            "question_type": f"Project: {proj} | Level 3 Deep | Scenario-Based"
        })
        
        questions.append({
            "question": f"What happens in '{proj}' if a user uploads a scanned image-based PDF instead of a text-based resume? How would you handle this scenario?",
            "answer_guideline": (
                f"Explain that text extractors (like PyPDF2) will return empty strings. "
                f"Suggest integrating OCR (like Tesseract/pytesseract) or validating document structure, reporting error states to the user.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- Explaining why standard PDF reader libraries extract zero characters from scanned documents\n"
                f"- Error boundary: detecting empty raw text early and throwing a custom user-facing exception\n"
                f"- Adding OCR logic: routing empty text files to a Tesseract OCR microservice engine\n"
                f"- User experience: displaying an actionable message advising them to upload a clean text-based file"
            ),
            "question_type": f"Project: {proj} | Level 3 Deep | Scenario-Based"
        })

    # Category E - Resume Claim Verification (Level 3 Deep)
    for idx, claim in enumerate(strong_claims[:2]):
        questions.append({
            "question": f"Your resume states: \"{claim}\". Walk me through the exact implementation details. What tools did you use, and how did you verify its accuracy?",
            "answer_guideline": (
                f"Explain your hands-on role in implementing this specific feature. Explain the software patterns used, "
                f"the metrics measured (e.g. latency, match rate, speed), and how you tested correctness.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- Explanation of what triggered the choice to build this feature\n"
                f"- The precise code layers, functions, or modules that handle this capability\n"
                f"- Quantifiable parameters or results that back up your success claim\n"
                f"- How you wrote unit or integration tests to assert that it functions correctly"
            ),
            "question_type": f"Claim Verification | Level 3 Deep | Verification"
        })

    # Fill up with a behavioral question if we have room
    if clean_exp:
        role = re.sub(r'^\s*[-•*\u2022]\s*', '', clean_exp[0]).split("-")[0].strip()
        questions.append({
            "question": f"During your role as '{role}', how did you deal with shifting priorities or tight sprint deadlines? Can you give a specific example?",
            "answer_guideline": (
                f"Use the STAR method. Describe the constraint, your strategy for prioritizing deliverables, how you communicated with "
                f"the team or lead, and the final successful launch.\n\n"
                f"**Key Talking Points to Include:**\n"
                f"- Situation: A specific task or feature release with overlapping dates\n"
                f"- Task: Balancing critical path bugs vs nice-to-have capabilities\n"
                f"- Action: Transparent communication with developers, scaling down scope, focusing on quality first\n"
                f"- Result: Delivering core features on schedule, planning technical debt tickets for later"
            ),
            "question_type": "Experience-Based | Level 2 Intermediate | Behavioral"
        })

    return {
        "resume_summary": resume_summary,
        "questions": questions
    }
