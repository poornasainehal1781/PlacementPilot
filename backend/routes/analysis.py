import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db, Resume, JobDescription, Analysis, InterviewQuestion
from backend.analyzer import analyze_resume_against_job
from backend.questions import generate_questions, extract_projects_from_text
from backend.deep_questions import generate_deep_questions
from backend.pdf_generator import generate_pdf_report

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_resume():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    resume_id = data.get('resume_id')
    job_title = data.get('job_title')
    job_description_text = data.get('job_description')

    if not resume_id or not job_title or not job_description_text:
        return jsonify({"error": "resume_id, job_title, and job_description are required"}), 400

    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    try:
        # 1. Parse and save Job Description
        from backend.parser import extract_skills
        jd_skills = extract_skills(job_description_text)
        
        job_desc = JobDescription(
            title=job_title,
            description=job_description_text
        )
        job_desc.set_skills(jd_skills)
        db.session.add(job_desc)
        db.session.flush() # Populate ID

        # 2. Run analysis
        resume_data = resume.to_dict()
        resume_data["raw_text"] = resume.raw_text
        analysis_result = analyze_resume_against_job(resume_data, job_title, job_description_text)

        # 3. Create Analysis Record
        analysis = Analysis(
            user_id=user_id,
            resume_id=resume.id,
            job_id=job_desc.id,
            ats_score=analysis_result["ats_score"],
            similarity_score=analysis_result["similarity_score"]
        )
        analysis.set_missing_skills(analysis_result["missing_skills"])
        analysis.set_recommendations(analysis_result["recommendations"])
        db.session.add(analysis)
        db.session.flush() # Populate ID

        # 4. Generate & Save Interview Questions
        try:
            deep_data = generate_deep_questions(resume_data, job_title, job_description_text)
        except Exception as q_err:
            print(f"[AnalysisRoute] Error calling generate_deep_questions: {q_err}")
            # Fallback to legacy generator in case of critical crash
            legacy_qs = generate_questions(resume_data["skills"], analysis_result["missing_skills"], resume_data)
            deep_data = {
                "resume_summary": {
                    "key_skills": resume_data["skills"],
                    "projects": [{"title": p, "technologies": [], "description": ""} for p in extract_projects_from_text(resume_data.get("raw_text", ""), resume_data.get("experience", []))],
                    "internship_highlights": resume_data.get("experience", []),
                    "strong_claims": []
                },
                "questions": legacy_qs
            }

        # Save resume summary in recommendations
        analysis_recs = analysis_result["recommendations"]
        analysis_recs["resume_summary"] = deep_data.get("resume_summary", {})
        analysis.set_recommendations(analysis_recs)

        generated_qs = deep_data.get("questions", [])
        db_questions = []
        for q in generated_qs:
            db_q = InterviewQuestion(
                analysis_id=analysis.id,
                question=q["question"],
                answer_guideline=q["answer_guideline"],
                question_type=q["question_type"]
            )
            db.session.add(db_q)
            db_questions.append(db_q)
            
        db.session.commit()

        return jsonify({
            "message": "Analysis completed successfully",
            "analysis": analysis.to_dict(),
            "job_description": job_desc.to_dict(),
            "questions": [q.to_dict() for q in db_questions]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@analysis_bp.route('/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    user_id = get_jwt_identity()
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).all()
    
    result = []
    for a in analyses:
        job = JobDescription.query.get(a.job_id)
        resume = Resume.query.get(a.resume_id)
        
        item = a.to_dict()
        item["job_title"] = job.title if job else "Unknown Role"
        item["resume_filename"] = resume.filename if resume else "Deleted Resume"
        result.append(item)
        
    return jsonify(result), 200

@analysis_bp.route('/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_details(analysis_id):
    user_id = get_jwt_identity()
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis record not found"}), 404

    job = JobDescription.query.get(analysis.job_id)
    resume = Resume.query.get(analysis.resume_id)
    questions = InterviewQuestion.query.filter_by(analysis_id=analysis.id).all()

    resume_dict = None
    if resume:
        resume_dict = resume.to_dict()
        from backend.parser import extract_name, extract_email, extract_phone
        resume_dict["name"] = extract_name(resume.raw_text)
        resume_dict["email"] = extract_email(resume.raw_text) or "No email detected"
        resume_dict["phone"] = extract_phone(resume.raw_text) or "No phone number detected"

    return jsonify({
        "analysis": analysis.to_dict(),
        "job_description": job.to_dict() if job else None,
        "resume": resume_dict,
        "questions": [q.to_dict() for q in questions]
    }), 200

@analysis_bp.route('/<int:analysis_id>/report', methods=['GET'])
@jwt_required()
def download_report(analysis_id):
    user_id = get_jwt_identity()
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis record not found"}), 404

    resume = Resume.query.get(analysis.resume_id)
    job = JobDescription.query.get(analysis.job_id)
    questions = InterviewQuestion.query.filter_by(analysis_id=analysis.id).all()

    if not resume or not job:
        return jsonify({"error": "Associated resume or job description was deleted"}), 400

    try:
        # Create a report folder
        reports_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_path = os.path.join(reports_dir, f"report_{analysis.id}.pdf")
        
        # Generate the PDF
        generate_pdf_report(analysis, resume, job, questions, pdf_path)
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"ATS_Report_{job.title.replace(' ', '_')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500
