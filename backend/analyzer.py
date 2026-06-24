import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.parser import extract_skills, COMMON_SKILLS

def calculate_similarity(resume_text, job_description_text):
    """
    Calculates the TF-IDF cosine similarity between the resume text and the job description.
    Returns a score between 0 and 100.
    """
    if not resume_text or not job_description_text:
        return 0.0
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text, job_description_text])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(similarity * 100)
    except Exception as e:
        print(f"[Analyzer] Error calculating cosine similarity: {e}")
        return 0.0

def generate_actionable_improvements(resume_data, missing_skills, job_description_text="", similarity_score=100.0):
    improvements = []
    
    resume_text = resume_data.get("raw_text", "")
    
    # 1. Contact/Header suggestions
    name = resume_data.get("name")
    email = resume_data.get("email")
    phone = resume_data.get("phone")
    
    if not name or name == "Unknown Candidate":
        from backend.parser import extract_name
        name = extract_name(resume_text)
    if not email:
        from backend.parser import extract_email
        email = extract_email(resume_text)
    if not phone:
        from backend.parser import extract_phone
        phone = extract_phone(resume_text)
        
    header_issues = []
    if not name or name == "Unknown Candidate":
        header_issues.append("full name")
    if not email:
        header_issues.append("email address")
    if not phone:
        header_issues.append("phone number")
        
    if header_issues:
        improvements.append({
            "where": "Header Section",
            "what": f"Add missing contact information: {', '.join(header_issues)}.",
            "how": "Place your professional full name, email address, and phone number at the top of the resume. Optionally add links to LinkedIn or GitHub."
        })
        
    # 2. Skills suggestions
    if missing_skills:
        top_missing = missing_skills[:5]
        improvements.append({
            "where": "Technical Skills Section",
            "what": f"Include missing critical job keywords: {', '.join(top_missing)}.",
            "how": f"Directly list **{', '.join(top_missing)}** under your skills section. This will optimize your resume for automated ATS search parsing."
        })
        
    # 3. Dynamic Job Description Term Matching (to increase similarity score)
    if job_description_text and similarity_score < 80.0:
        # Extract important words from JD that don't appear in the resume
        from backend.parser import get_nlp
        nlp = get_nlp()
        doc_jd = nlp(job_description_text)
        
        jd_words = set()
        for token in doc_jd:
            # Find meaningful nouns/adjectives that are not stop words
            if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and len(token.text) > 3:
                w_lower = token.text.lower()
                if not w_lower.isdigit() and w_lower not in ["year", "years", "role", "team", "member", "work", "job", "candidate", "position", "seeking", "requirements"]:
                    jd_words.add(token.text.lower())
                    
        resume_lower = resume_text.lower()
        missing_terms = [w for w in jd_words if w not in resume_lower]
        
        # Sort by length or just take the top ones
        missing_terms.sort(key=len, reverse=True)
        
        if missing_terms:
            top_terms = missing_terms[:6]
            # Map back to how they appeared in the text (for capitalization)
            display_terms = []
            for t in top_terms:
                matches = re.findall(rf'\b{re.escape(t)}\b', job_description_text, re.IGNORECASE)
                if matches:
                    display_terms.append(matches[0])
                else:
                    display_terms.append(t.title())
            
            # Deduplicate keeping order
            display_terms = list(dict.fromkeys(display_terms))
            
            improvements.append({
                "where": "Experience / Projects Context",
                "what": f"Weave missing job terms into bullet points: {', '.join(display_terms)}.",
                "how": f"To increase your ATS semantic similarity score (currently {similarity_score:.1f}%), weave these terms directly into your experience or project bullet points."
            })

    # 4. Experience & Bullet point updates
    experience_items = resume_data.get("experience", [])
    has_experience = len(experience_items) > 0
    
    if not has_experience:
        improvements.append({
            "where": "Work Experience Section",
            "what": "Add a dedicated Work Experience section.",
            "how": "Insert chronological roles detailing job titles, companies, dates, and bulleted achievements starting with active verbs."
        })
    else:
        # Scan experience items for optimization
        enhanced_count = 0
        for item in experience_items:
            item_clean = item.strip()
            item_lower = item_clean.lower()
            
            # Look for React/Python/Flask bullet point to optimize
            if "react" in item_lower or "flask" in item_lower or "python" in item_lower:
                if len(item_clean) < 100:  # If it's a bit short/basic
                    improvements.append({
                        "where": "Work Experience (Recent Role)",
                        "what": f"Elaborate on tech stack bullet: '{item_clean}'",
                        "how": "Rewrite to add scope and impact. Suggested format: 'Architected and built interactive frontend components using React, interfacing with Python/Flask REST APIs, which improved page load performance by 25% and streamlined user workflows.'"
                    })
                    enhanced_count += 1
                    break
                    
        for item in experience_items:
            item_clean = item.strip()
            item_lower = item_clean.lower()
            if "sql" in item_lower or "database" in item_lower or "query" in item_lower:
                if len(item_clean) < 80:
                    improvements.append({
                        "where": "Work Experience (Database Contributions)",
                        "what": f"Add quantitative metrics to query optimization: '{item_clean}'",
                        "how": "Quantify your database contribution. Suggested format: 'Optimized database schemas and indexed frequent SQL queries, reducing search latency by 45% and increasing backend database transaction throughput.'"
                    })
                    enhanced_count += 1
                    break
                    
        # Always suggest adding strong action verbs and quantitative metrics if similarity score is low
        if similarity_score < 80.0:
            improvements.append({
                "where": "Work Experience Section",
                "what": "Quantify accomplishments and start bullet points with Action Verbs.",
                "how": "Rewrite experience bullet points using the Google X-Y-Z formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. Start each bullet with verbs like 'Spearheaded', 'Optimized', or 'Designed' and include quantitative impact (e.g. 'reduced latency by 30%')."
            })
            
    # 5. Education suggestions
    education_items = resume_data.get("education", [])
    if not education_items:
        improvements.append({
            "where": "Education Section",
            "what": "Add an Education section.",
            "how": "State your highest degree, major, institution, and graduation year to complete the academic background expected by recruiters."
        })
        
    return improvements

def analyze_resume_against_job(resume_data, job_title, job_description):
    """
    Compares parsed resume data against a job description.
    Returns details on scores, keyword match, and structural feedback.
    """
    resume_text = resume_data.get("raw_text", "")
    resume_skills = set(resume_data.get("skills", []))
    
    # Extract skills from job description using the same vocabulary
    jd_skills = set(extract_skills(job_description))
    
    # If no skills are detected in the job description, try to extract some noun chunks
    if not jd_skills:
        # Fallback: look for common technical/soft words from general vocabulary
        jd_skills_detected = []
        jd_lower = job_description.lower()
        for skill in COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if skill in ["c++", "c#"]:
                pattern = re.escape(skill)
            if re.search(pattern, jd_lower):
                jd_skills_detected.append(skill)
        jd_skills = set(jd_skills_detected)
        
    # Calculate skill match metrics
    if jd_skills:
        matched_skills = list(resume_skills.intersection(jd_skills))
        missing_skills = list(jd_skills.difference(resume_skills))
        skill_match_score = (len(matched_skills) / len(jd_skills)) * 100
    else:
        matched_skills = list(resume_skills)
        missing_skills = []
        skill_match_score = 100.0 # No skills in JD, perfect default match
 
    # Calculate overall similarity
    cosine_score = calculate_similarity(resume_text, job_description)
    
    # Calculate structural/completeness score (max 100)
    structure_score = 0
    structure_recs = []
    
    # Dynamic contact parsing fallback
    name = resume_data.get("name")
    email = resume_data.get("email")
    phone = resume_data.get("phone")
    
    if not name or name == "Unknown Candidate":
        from backend.parser import extract_name
        name = extract_name(resume_text)
    if not email:
        from backend.parser import extract_email
        email = extract_email(resume_text)
    if not phone:
        from backend.parser import extract_phone
        phone = extract_phone(resume_text)
        
    if name and name != "Unknown Candidate":
        structure_score += 20
    else:
        structure_recs.append("Add a professional name at the top of your resume.")
        
    if email:
        structure_score += 20
    else:
        structure_recs.append("Include your email address so recruiters can contact you.")
        
    if phone:
        structure_score += 20
    else:
        structure_recs.append("Include your phone number for interview scheduling.")
        
    if resume_data.get("experience") and len(resume_data.get("experience")) > 0:
        structure_score += 20
    else:
        structure_recs.append("Add a dedicated Work Experience section with dates.")
        
    if resume_data.get("education") and len(resume_data.get("education")) > 0:
        structure_score += 20
    else:
        structure_recs.append("Add an Education section highlighting your academic background.")
 
    # Calculate final weighted ATS Score
    # 50% Skill/Keyword Match, 30% Contextual Cosine Similarity, 20% Structure & Contact Info
    ats_score = (skill_match_score * 0.5) + (cosine_score * 0.3) + (structure_score * 0.2)
    ats_score = round(min(100.0, max(0.0, ats_score)), 1)
    
    # Compile recommendations
    recommendations = {
        "formatting_suggestions": structure_recs,
        "critical_skills_to_add": missing_skills[:6], # Suggest top 6 missing skills
        "general_feedback": "",
        "actionable_improvements": generate_actionable_improvements(
            resume_data, 
            missing_skills, 
            job_description_text=job_description, 
            similarity_score=cosine_score
        )
    }
    
    if ats_score >= 80:
        recommendations["general_feedback"] = "Excellent match! Your resume aligns highly with the job description. Ready to apply."
    elif ats_score >= 60:
        recommendations["general_feedback"] = "Good match, but has room for improvement. Add the missing key skills and ensure your experience highlights project outcomes."
    else:
        recommendations["general_feedback"] = "Low alignment. We strongly recommend rewriting sections of your resume to include the missing skills and matching your vocabulary to the job description."
 
    return {
        "ats_score": ats_score,
        "similarity_score": round(cosine_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations
    }
