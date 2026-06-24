# Predefined pool of high-quality interview questions and guidelines

QUESTION_BANK = {
    "python": [
        {
            "question": "How are arguments passed in Python (by value or by reference)?",
            "answer_guideline": "Explain that Python uses 'pass-by-assignment' (or call-by-sharing). Mutable objects (like lists or dicts) can be modified in-place, whereas immutable objects (like integers, strings, tuples) cannot. Use code snippets in your explanation if possible."
        },
        {
            "question": "What is the difference between list and tuple in Python? When would you use which?",
            "answer_guideline": "Explain that lists are mutable (can be changed) and tuples are immutable. Tuples are generally faster and can be used as dictionary keys. Mention that tuples signify heterogeneous data structures, while lists signify homogeneous sequences."
        },
        {
            "question": "What is a decorator in Python, and how is it useful?",
            "answer_guideline": "Explain decorators as wrappers around functions that modify their behavior without changing the code itself. Mention common use cases like logging, authorization, and caching."
        }
    ],
    "javascript": [
        {
            "question": "Explain the concept of closures in JavaScript.",
            "answer_guideline": "Define a closure as a function that remembers its outer variables even after the outer function has finished executing. Give a simple counter example, and explain how it helps with data encapsulation."
        },
        {
            "question": "What is the event loop in JavaScript, and how does it handle asynchronous code?",
            "answer_guideline": "Explain that JavaScript is single-threaded but handles asynchronous operations via the Call Stack, Web APIs, Callback Queue, and the Event Loop. Mention how promises/microtasks have higher priority than standard callbacks."
        }
    ],
    "react": [
        {
            "question": "What are React hooks, and what rules must be followed when using them?",
            "answer_guideline": "Explain hooks (useState, useEffect, etc.) allow function components to use state and lifecycle features. Mention the rules: 1. Only call hooks at the top level (not inside loops or conditions). 2. Only call hooks from React functional components."
        },
        {
            "question": "How does the Virtual DOM work in React, and how does it improve performance?",
            "answer_guideline": "Explain that React keeps a lightweight representation of the real DOM in memory. When state changes, a new virtual DOM is created. React compares the new virtual DOM with the previous one (diffing) and updates only the changed parts of the real DOM (reconciliation)."
        }
    ],
    "sql": [
        {
            "question": "What is the difference between inner join, left join, and outer join?",
            "answer_guideline": "Explain: INNER JOIN returns matched rows in both tables. LEFT JOIN returns all rows from the left table and matched rows from the right. OUTER JOIN (or FULL OUTER JOIN) returns rows from either table where there is a match."
        },
        {
            "question": "What are database indexes, and how do they speed up queries? Are there any downsides?",
            "answer_guideline": "Explain indexes are data structures (like B-trees) that allow fast searching. Downside: they take up disk space and slow down write operations (INSERT, UPDATE, DELETE) since the index must also be updated."
        }
    ],
    "docker": [
        {
            "question": "What is the difference between a Docker image and a Docker container?",
            "answer_guideline": "Explain that an image is a read-only template containing instructions/binaries for creating a container. A container is a runnable instance of an image. Use the analogy: Image is class, Container is instance."
        }
    ],
    "aws": [
        {
            "question": "What is the difference between horizontal and vertical scaling in AWS?",
            "answer_guideline": "Explain: Vertical scaling (scaling up) means adding more power (CPU, RAM) to an existing instance. Horizontal scaling (scaling out) means adding more instances (EC2 machines) behind a load balancer. Mention Auto Scaling groups."
        }
    ],
    "git": [
        {
            "question": "What is the difference between git merge and git rebase?",
            "answer_guideline": "Explain that 'merge' combines changes from different branches and creates a merge commit, preserving historical timeline. 'rebase' moves the entire branch starting point to a new commit, creating a clean linear history but rewriting commits."
        }
    ],
    "machine learning": [
        {
            "question": "Explain the difference between overfitting and underfitting in ML, and how to prevent them.",
            "answer_guideline": "Overfitting: high training accuracy, poor test accuracy (model learns noise). Prevent via regularization, more data, cross-validation. Underfitting: low training and test accuracy (model too simple). Prevent via complex model, adding features, reducing regularization."
        }
    ],
    "agile": [
        {
            "question": "What are the core ceremonies in the Scrum framework?",
            "answer_guideline": "Explain the 4 standard ceremonies: Sprint Planning (define sprint goals), Daily Standup (15-min sync), Sprint Review (demo work to stakeholders), and Sprint Retrospective (reflect on team improvement)."
        }
    ]
}

BEHAVIORAL_QUESTIONS = [
    {
        "question": "Tell me about a time you faced a difficult technical challenge. How did you resolve it?",
        "answer_guideline": "Use the STAR method. S: Describe a complex project/bug. T: Identify your specific task. A: Detail how you troubleshooted (logs, docs, isolation). R: Explain the successful outcome and what you learned."
    },
    {
        "question": "Describe a situation where you had a conflict with a team member or stakeholder. How did you handle it?",
        "answer_guideline": "Focus on communication and empathy. S: Describe a difference of opinion. T: Objective to resolve it professionally. A: Explain how you set up a private meeting, listened to their perspective, and found a compromise. R: Positive relationship restored and project delivered."
    },
    {
        "question": "How do you handle tight deadlines or shifting priorities?",
        "answer_guideline": "Emphasize prioritization and stakeholder management. Explain that you list tasks, evaluate critical paths, communicate constraints early, and adjust scope if necessary, ensuring quality is maintained."
    },
    {
        "question": "Describe a time you made a mistake on a project. What did you do to fix it?",
        "answer_guideline": "Show accountability. S: Explain the mistake. T: The immediate corrective action needed. A: Explain how you notified the lead immediately, formulated a fix, deployed it safely, and added test cases to prevent recurrence. R: Minimal impact, lessons learned."
    }
]

GENERAL_QUESTIONS = [
    {
        "question": "Explain how you handle web security (e.g. SQL Injection, XSS, CSRF) in your applications.",
        "answer_guideline": "Explain: SQL Injection is prevented by parameterized queries/ORMs. XSS by escaping inputs and using Content Security Policy (CSP). CSRF by anti-CSRF tokens and using modern secure cookie flags (SameSite=Strict)."
    },
    {
        "question": "How do you design a scalable REST API?",
        "answer_guideline": "Talk about standard HTTP methods (GET, POST, PUT, DELETE), proper status codes, versioning (/api/v1), pagination, caching, and rate limiting."
    }
]

def extract_projects_from_text(text, experience=None):
    """
    Identifies projects mentioned in the resume text or experience list.
    Returns a list of parsed project names/descriptions.
    """
    import re
    if not text:
        return []
        
    lines = text.split("\n")
    project_keywords = ["projects", "personal projects", "academic projects", "key projects", "key initiatives", "notable projects"]
    
    proj_list = []
    is_proj_section = False
    
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
        if is_proj_section and any(ekey in line_lower for ekey in ["experience", "education", "skills", "work history", "certifications", "interests", "languages"]) and len(line_clean) < 30:
            is_proj_section = False
            break
            
        if is_proj_section:
            # Avoid headings or very short lines
            if len(line_clean) > 15 and not line_clean.isupper() and not line_clean.endswith(":"):
                proj_list.append(line_clean)
                
    # If no project section was detected, extract from experience items
    if not proj_list and experience:
        for exp in experience:
            exp_clean = exp.strip()
            exp_lower = exp_clean.lower()
            if any(verb in exp_lower for verb in ["developed", "built", "designed", "implemented", "engineered", "project"]):
                if len(exp_clean) > 20 and len(exp_clean) < 150:
                    proj_list.append(exp_clean)
                    
    # Fallback to general lines in raw text containing project-like verbs
    if not proj_list:
        action_verbs = ["developed", "built", "designed", "implemented", "engineered"]
        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            if any(line_lower.startswith(verb) or f" {verb} " in line_lower for verb in action_verbs):
                if len(line_clean) > 20 and len(line_clean) < 150:
                    proj_list.append(line_clean)
                    if len(proj_list) >= 5:
                        break
                        
    # Ensure items are unique
    seen = set()
    unique_proj = []
    for p in proj_list:
        p_clean = re.sub(r'^\s*[-•*]\s*', '', p) # remove leading bullet characters
        if p_clean.lower() not in seen:
            seen.add(p_clean.lower())
            unique_proj.append(p_clean)
            
    return unique_proj[:6]

def extract_custom_resume_bullets(raw_text):
    """
    Scans the raw text of the resume line by line to identify specific kinds of experience/achievement statements:
    1. Quantitative / Performance Achievements
    2. Leadership / Mentorship / Collaboration roles
    3. Advanced tool/infrastructure usages (e.g. Redis, Kafka, Elasticsearch, Docker, Kubernetes, Terraform)
    """
    import re
    if not raw_text:
        return {"achievements": [], "leadership": [], "advanced_tools": []}

    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    
    achievements = []
    leadership = []
    advanced_tools = []
    
    # Pre-compile regex patterns
    # Quantitative: contains digits or %, and keywords like reduced, improved, optimized, increased, saved, designed, built, etc.
    quant_verbs = r'(?:reduc|improv|optimiz|increas|sav|cut|boost|generat|scal|develop|built|creat|design|launch)'
    quant_pattern = re.compile(rf'\b{quant_verbs}\w*\b.*\b(?:\d+%|\d+\s*percent|\$\s*\d+|\d+\s*x|\d+\s*hours|\d+\s*months|\b(?:million|billion|thousand|hundreds|tens)\b|\b(?:percent|percentage)\b)', re.IGNORECASE)
    
    # Leadership: contains led, mentored, managed, supervised, trained, spearheaded, coordinate, collaborate
    lead_pattern = re.compile(r'\b(?:led|leader|mentored|mentor|managed|manager|spearheaded|supervised|trained|coordinated|directed|oversaw|guided|collaborated)\b', re.IGNORECASE)
    
    # Advanced infrastructure/tools keywords
    advanced_keywords = ["redis", "kafka", "elasticsearch", "elastic search", "kubernetes", "k8s", "terraform", "graphql", "serverless", "lambda", "aws", "gcp", "azure", "ci/cd", "jenkins", "github actions", "microservices", "docker", "ansible"]
    
    for line in lines:
        # Clean leading bullets
        clean_line = re.sub(r'^\s*[-•*\u2022]\s*', '', line).strip()
        if len(clean_line) < 20 or len(clean_line) > 200:
            continue
            
        # 1. Check achievements
        if quant_pattern.search(clean_line):
            achievements.append(clean_line)
            
        # 2. Check advanced tools
        line_lower = clean_line.lower()
        matched_tools = [tool for tool in advanced_keywords if re.search(rf'\b{re.escape(tool)}\b', line_lower)]
        if matched_tools:
            advanced_tools.append((clean_line, matched_tools))
            
        # 3. Check leadership
        if lead_pattern.search(clean_line):
            leadership.append(clean_line)

    return {
        "achievements": list(dict.fromkeys(achievements)), # Deduplicate keeping order
        "leadership": list(dict.fromkeys(leadership)),
        "advanced_tools": advanced_tools # Keep list of tuples (line, matched_tools)
    }

def generate_questions(resume_skills, missing_skills, resume_data=None):
    """
    Generates dynamic interview questions tailored specifically to the candidate's skills,
    experience, and projects.
    """
    import re
    tech_qs = []
    
    # 1. Extract raw text, experience, and projects
    raw_text = ""
    experience = []
    projects = []
    role_title = "Developer"
    company_name = "your recent employer"
    
    if resume_data:
        raw_text = resume_data.get("raw_text", "")
        experience = resume_data.get("experience", [])
        projects = extract_projects_from_text(raw_text, experience)
        
        # Identify role title and company from experience if possible
        if experience:
            # Look for a line containing common role indicators and avoiding description bullet characters
            role_line = None
            role_keywords = ["developer", "engineer", "intern", "manager", "analyst", "consultant", "specialist", "designer", "architect", "lead", "programmer", "internship"]
            for exp in experience:
                exp_lower = exp.lower()
                if any(kw in exp_lower for kw in role_keywords):
                    if not exp.strip().startswith(("\u2022", "•", "-", "*")):
                        role_line = exp
                        break
            
            if not role_line:
                for exp in experience:
                    if not exp.strip().startswith(("\u2022", "•", "-", "*")):
                        role_line = exp
                        break
                if not role_line:
                    role_line = experience[0]
                    
            if role_line:
                cleaned_line = role_line.replace("—", "-").replace("–", "-")
                cleaned_line = re.sub(r'^\s*[-•*\u2022]\s*', '', cleaned_line)
                parts = [p.strip() for p in cleaned_line.split("-")]
                if len(parts) >= 2:
                    role_title = parts[0]
                    company_part = parts[1]
                    company_part = re.sub(r'\d{4}.*$', '', company_part)
                    company_part = re.sub(r'\s*\(.*\)\s*$', '', company_part)
                    company_name = company_part.strip()
                else:
                    match_at = re.search(r'([a-zA-Z\s&]+)\s+at\s+([a-zA-Z\s\.]+)', role_line, re.IGNORECASE)
                    if match_at:
                        role_title = match_at.group(1).strip()
                        company_name = match_at.group(2).strip()
                    else:
                        words = role_line.split()
                        if len(words) >= 2:
                            role_title = " ".join(words[:2])
                            company_name = " ".join(words[2:])
                            
    # 2. Extract specific achievements, leadership, and tool usage from the raw text
    # 2. Extract specific achievements, leadership, and tool usage from the raw text
    custom_bullets = extract_custom_resume_bullets(raw_text)
    custom_achievements = custom_bullets["achievements"]
    custom_leadership = custom_bullets["leadership"]
    custom_advanced_tools = custom_bullets["advanced_tools"]

    asked_lines = set()

    # 3. Build technical / project questions
    # Prioritize question based on parsed achievements
    if custom_achievements:
        ach = custom_achievements[0]
        tech_qs.append({
            "question": f"Looking at your experience, I noticed you mentioned: \"{ach}\". Could you tell me a bit more about the baseline situation before you stepped in, the technical approach you took to drive this outcome, and how you quantified that success?",
            "answer_guideline": "The candidate should: 1. Detail the baseline metrics and target goals. 2. Explain the troubleshooting/design process. 3. Discuss the implementation and specific technologies. 4. State the final measurable results and impact.",
            "question_type": "Technical (Achievement)"
        })
        asked_lines.add(ach)

    # Prioritize question based on advanced tools matched in specific lines
    unused_advanced_tools = [t for t in custom_advanced_tools if t[0] not in asked_lines]
    if unused_advanced_tools:
        line, matched = unused_advanced_tools[0]
        tools_str = " & ".join([t.upper() for t in matched])
        tech_qs.append({
            "question": f"Your resume mentions: \"{line}\". What was the architectural rationale behind choosing {tools_str} in this context, and what were the main engineering tradeoffs or alternative options you considered?",
            "answer_guideline": f"Evaluate: 1. The reason for choosing {tools_str} (e.g. pub/sub, scaling, schema-less, caching). 2. Performance or security tradeoffs (e.g. complexity, memory overhead). 3. Alternative technical stacks considered.",
            "question_type": "Technical (Architecture)"
        })
        asked_lines.add(line)

    # If we still have space or don't have enough custom questions, use project system design questions
    if len(tech_qs) < 2 and len(projects) > 0:
        proj = projects[0]
        mentioned_skills = [s for s in resume_skills if s.lower() in proj.lower()]
        tech_qs.append({
            "question": f"I'd love to dive into your project '{proj}'. Could you walk me through the high-level system architecture you designed, and share some of the trickiest technical challenges you ran into while building it?",
            "answer_guideline": f"The candidate should describe: 1. Core modules and components. 2. Data flow between frontend, backend, and database. 3. Tradeoffs made (e.g. choice of technologies like {', '.join(mentioned_skills) if mentioned_skills else 'Python/React'}). 4. Key challenges resolved during development.",
            "question_type": "Technical (System Design)"
        })

    if len(tech_qs) < 3 and len(projects) > 1:
        proj = projects[1]
        tech_qs.append({
            "question": f"For that same project '{proj}', how did you identify and handle performance bottlenecks or latency issues? What specific optimization techniques did you put in place to ensure it scales well?",
            "answer_guideline": "Evaluate their experience in: 1. Profiling and debugging bottlenecks. 2. Backend scaling, database indexing, caching strategies, or asset bundling. 3. Quantitative results of optimization if any.",
            "question_type": "Technical (Optimization)"
        })
    elif len(tech_qs) < 3 and len(experience) > 1:
        tech_qs.append({
            "question": f"In your role where you '{experience[1]}', how did you verify that the solution would scale and perform under load? What kind of testing methodologies or monitoring tools did you set up?",
            "answer_guideline": "Look for answers mentioning: 1. Load testing or stress testing (e.g. JMeter, Locust). 2. Performance profiling of endpoints or functions. 3. Monitoring tools (APM, dashboards) and database scaling.",
            "question_type": "Technical (Scalability)"
        })

    # Deep dive into skill-specific technical questions based on their resume skills
    skills_to_dive = [s for s in resume_skills if s.lower() in ["python", "javascript", "typescript", "react", "sql", "flask", "docker", "aws"]]
    if not skills_to_dive:
        skills_to_dive = resume_skills[:2]
        
    for skill in skills_to_dive[:2]:
        if len(tech_qs) >= 4:
            break
        if skill.lower() == "python":
            tech_qs.append({
                "question": "I see Python listed as one of your core languages. When dealing with concurrency or asynchronous workloads in Python, how do you decide whether to use asyncio, threading, or multiprocessing for your tasks?",
                "answer_guideline": "The candidate should discuss: 1. The Global Interpreter Lock (GIL) and its implications. 2. When to use asyncio/threading for I/O bound tasks vs multiprocessing for CPU-bound tasks. 3. Libraries or frameworks used.",
                "question_type": "Technical (Python)"
            })
        elif skill.lower() == "react":
            tech_qs.append({
                "question": "In your React applications, how do you design your state management to keep components rendering efficiently? Under what conditions do you find Context API sufficient versus bringing in Redux or Zustand?",
                "answer_guideline": "Evaluate understanding of: 1. React reconciliation and render cycle. 2. Hook usage (useMemo, useCallback). 3. Context API limitations (unnecessary re-renders) vs specialized state managers (Redux/Zustand slice selectors).",
                "question_type": "Technical (React)"
            })
        elif skill.lower() in ["sql", "mysql", "postgresql", "sqlite"]:
            tech_qs.append({
                "question": f"Since you have solid experience with {skill}, could you walk me through your process for diagnosing and optimizing a slow-running query? How do you leverage execution plans and database indexes to boost performance?",
                "answer_guideline": "Look for: 1. Execution plans (EXPLAIN output analysis, table scans vs index scans). 2. Composite indexes and leftmost prefix rule. 3. Tradeoffs of indexes on write performance.",
                "question_type": f"Technical ({skill})"
            })
        else:
            tech_qs.append({
                "question": f"You highlight proficiency in {skill}. Could you share a particularly tricky technical bug or issue you resolved using {skill}, and explain the step-by-step logic you used to solve it?",
                "answer_guideline": f"The candidate should show deep expertise in {skill} by: 1. Detailing a specific bug/incident. 2. Debugging methodology. 3. System details related to {skill}. 4. Prevention of regression.",
                "question_type": f"Technical ({skill})"
            })

    # Add missing skill preparation question if there is a gap
    if missing_skills:
        for skill in missing_skills[:2]:
            if len(tech_qs) >= 4:
                break
            tech_qs.append({
                "question": f"We're looking for experience with {skill}, which isn't explicitly listed on your resume. Based on your work with similar stacks, how would you approach designing a simple microservice or integration using {skill}?",
                "answer_guideline": f"The candidate should bridge their existing technical knowledge to {skill}, showing adaptability, quick learning, and understanding of the core concepts of {skill}.",
                "question_type": f"Technical Prep ({skill})"
            })

    # Ensure we have at least 4 tech questions
    while len(tech_qs) < 4:
        if len(tech_qs) == 2:
            tech_qs.append({
                "question": "If you were tasked with designing a highly scalable and secure REST API from scratch to handle heavy traffic, what key architectural patterns and security measures would you implement?",
                "answer_guideline": "Look for: 1. API gateway, load balancing, stateless design. 2. Authentication (JWT), rate limiting. 3. Caching (Redis), database pooling.",
                "question_type": "Technical (General)"
            })
        else:
            tech_qs.append({
                "question": "Could you talk about your general philosophy when it comes to automated testing? How do you strike a balance between unit, integration, and E2E tests, and how do you handle mocking external APIs?",
                "answer_guideline": "Check for: 1. Unit testing frameworks. 2. Mocking/stubbing HTTP requests and database calls. 3. CI/CD test automation pipelines.",
                "question_type": "Technical (Testing)"
            })

    # Select up to 4 technical questions
    selected_tech = tech_qs[:4]

    # 4. Generate tailored behavioral questions
    beh_qs = []
    
    # Prioritize custom leadership questions
    unused_leadership = [l for l in custom_leadership if l not in asked_lines]
    if unused_leadership:
        lead_line = unused_leadership[0]
        beh_qs.append({
            "question": f"I was reading through your achievements and noticed this bullet: \"{lead_line}\". Tell me about the leadership or collaboration strategies you used there. How did you coordinate the team's efforts, handle delegation, and keep everyone on track?",
            "answer_guideline": "Assess: 1. Effective delegation and goal setting. 2. Fostering communication and collaboration. 3. Overcoming hurdles or differences in opinion (STAR method).",
            "question_type": "Behavioral (Leadership)"
        })
        asked_lines.add(lead_line)
    elif custom_leadership:
        lead_line = custom_leadership[0]
        beh_qs.append({
            "question": f"I was reading through your achievements and noticed this bullet: \"{lead_line}\". Tell me about the leadership or collaboration strategies you used there. How did you coordinate the team's efforts, handle delegation, and keep everyone on track?",
            "answer_guideline": "Assess: 1. Effective delegation and goal setting. 2. Fostering communication and collaboration. 3. Overcoming hurdles or differences in opinion (STAR method).",
            "question_type": "Behavioral (Leadership)"
        })

    # Fallback/Additional Q1: Team collaboration & engineering conflicts in the specific role
    if len(beh_qs) < 1:
        beh_qs.append({
            "question": f"During your time as a {role_title} at {company_name}, did you ever have a difference of opinion with another developer regarding a technical decision? How did you go about resolving that conflict and deciding on a path forward?",
            "answer_guideline": "Look for: 1. Respectful communication and listening. 2. Using objective data/benchmarks to resolve debates. 3. Seeking compromise or senior guidance if needed. 4. Commitment to the final decision (STAR method).",
            "question_type": "Behavioral"
        })
        
    # Q2: Deadlines/Tradeoffs on a specific project or achievement
    proj_name = projects[0] if projects else "your recent project"
    unused_achievements = [a for a in custom_achievements if a not in asked_lines]
    if unused_achievements:
        ach_alt = unused_achievements[0]
        beh_qs.append({
            "question": f"Thinking back to your work on: \"{ach_alt}\", what were the main execution constraints or deadline pressures you faced? How did you prioritize your workload to deliver high-quality code on time?",
            "answer_guideline": "Look for: 1. Clear prioritization and roadmap definition. 2. Trade-offs between speed and quality. 3. Stakeholder management and risk mitigation (STAR method).",
            "question_type": "Behavioral (Time Management)"
        })
    elif custom_achievements and len(custom_achievements) > 1:
        ach_alt = custom_achievements[1]
        beh_qs.append({
            "question": f"Thinking back to your work on: \"{ach_alt}\", what were the main execution constraints or deadline pressures you faced? How did you prioritize your workload to deliver high-quality code on time?",
            "answer_guideline": "Look for: 1. Clear prioritization and roadmap definition. 2. Trade-offs between speed and quality. 3. Stakeholder management and risk mitigation (STAR method).",
            "question_type": "Behavioral (Time Management)"
        })
    else:
        beh_qs.append({
            "question": f"For that project '{proj_name}', how did you manage tight deadlines or shifting requirements? Could you share a specific tradeoff you had to make between code quality and speed of delivery?",
            "answer_guideline": "Evaluate: 1. prioritization of critical features. 2. Managing technical debt consciously. 3. Communication with product owners/leads. 4. Positive delivery outcomes (STAR method).",
            "question_type": "Behavioral"
        })

    # Select 2 behavioral questions
    selected_beh = beh_qs[:2]

    # Generate tailored introductory questions (e.g. self intro, motivation)
    intro_qs = [
        {
            "question": f"Thanks for taking the time to speak with me today. To kick things off, could you walk me through your background and introduce yourself? I'd love to hear a bit about your experience as a {role_title} at {company_name} and some of the key projects you've worked on.",
            "answer_guideline": "The candidate should: 1. Keep it structured (e.g. past, present, future). 2. Keep it concise (under 2 minutes). 3. Highlight key achievements from their resume. 4. Match their response to their career aspirations.",
            "question_type": "Introduction (Self Intro)"
        },
        {
            "question": "I'd love to know what caught your eye about this specific position. How do you see your background and technical skills aligning with what we're looking to build in this role?",
            "answer_guideline": "Look for: 1. Clear motivation for applying. 2. Demonstration of understanding the role requirements. 3. Connection between past experience and the company's domain.",
            "question_type": "Introduction (Motivation)"
        }
    ]

    # Combine
    final_qs = intro_qs + selected_tech + selected_beh
    
    # Sort questions by difficulty (Easy -> Medium -> Hard)
    difficulty_map = {
        "Introduction": 5,
        "Behavioral": 10,
        "Technical Prep": 25,
        "Technical (Testing)": 30,
        "Technical (General)": 35,
        "Technical (Python)": 40,
        "Technical (React)": 40,
        "Technical (SQL)": 40,
        "Technical (JavaScript)": 40,
        "Technical (TypeScript)": 40,
        "Technical (Flask)": 40,
        "Technical (Docker)": 40,
        "Technical (AWS)": 40,
        "Technical (Optimization)": 50,
        "Technical (Scalability)": 55,
        "Technical (System Design)": 70,
        "Technical (Architecture)": 80,
        "Technical (Achievement)": 90
    }
    
    def get_difficulty(q):
        q_type = q.get("question_type", "")
        for key, val in difficulty_map.items():
            if q_type.startswith(key) or key in q_type:
                return val
        return 50  # Default medium difficulty
        
    final_qs.sort(key=get_difficulty)
    
    return final_qs

