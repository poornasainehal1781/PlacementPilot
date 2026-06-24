from collections import Counter
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db, Resume, Analysis, JobDescription

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    user_id = get_jwt_identity()

    # 1. Total Resumes
    total_resumes = Resume.query.filter_by(user_id=user_id).count()

    # 2. Total Analyses
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.asc()).all()
    total_analyses = len(analyses)

    # 3. Average ATS Score & Score History
    avg_score = 0
    score_history = []
    missing_skills_counter = Counter()

    if total_analyses > 0:
        total_score = 0
        for a in analyses:
            total_score += a.ats_score
            
            # Retrieve Job Description info for naming in chart
            job = JobDescription.query.get(a.job_id)
            job_title = job.title if job else "Unknown Role"
            
            # Format date: 'YYYY-MM-DD'
            date_str = a.created_at.strftime('%Y-%m-%d')
            
            score_history.append({
                "id": a.id,
                "date": date_str,
                "score": a.ats_score,
                "job_title": job_title
            })
            
            # Count missing skills
            missing_skills = a.get_missing_skills()
            for skill in missing_skills:
                missing_skills_counter[skill] += 1

        avg_score = round(total_score / total_analyses, 1)

    # 4. Top Missing Skills Frequency (for visualization)
    top_missing_skills = []
    for skill, count in missing_skills_counter.most_common(6):
        top_missing_skills.append({
            "skill": skill,
            "count": count
        })

    # Calculate Readiness Level
    readiness = "Low"
    if avg_score >= 80:
        readiness = "High"
    elif avg_score >= 60:
        readiness = "Moderate"
    elif total_analyses == 0:
        readiness = "N/A"

    return jsonify({
        "total_resumes": total_resumes,
        "total_analyses": total_analyses,
        "average_ats_score": avg_score,
        "readiness_level": readiness,
        "score_history": score_history,
        "top_missing_skills": top_missing_skills
    }), 200
