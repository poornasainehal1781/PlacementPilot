import re
import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db, Analysis, InterviewQuestion, ChatSession, ChatMessage, JobDescription, Resume

chat_bp = Blueprint('chat', __name__)

def evaluate_answer(student_answer, guideline):
    # Stop words to ignore when extracting keywords from the guideline
    stop_words = {
        "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", 
        "at", "by", "for", "with", "about", "against", "between", "into", 
        "through", "during", "before", "after", "above", "below", "to", 
        "from", "up", "down", "in", "out", "on", "off", "over", "under", 
        "again", "further", "then", "once", "here", "there", "when", 
        "where", "why", "how", "all", "any", "both", "each", "few", 
        "more", "most", "other", "some", "such", "no", "nor", "not", 
        "only", "own", "same", "so", "than", "too", "very", "can", 
        "will", "just", "should", "now", "explain", "describe", "discuss", 
        "mention", "detail", "discussing", "describing", "explaining", 
        "guideline", "candidate", "response", "answer", "question", 
        "structured", "strategy", "provide", "give", "example", "method", 
        "approach", "process", "using", "should", "your", "its", "their",
        "they", "them"
    }
    
    # Extract words of length >= 4 from guideline
    guideline_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', guideline.lower()))
    keywords = guideline_words.difference(stop_words)
    
    if not keywords:
        keywords = {"explanation", "detail", "approach", "results"}
        
    student_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', student_answer.lower()))
    
    matched = keywords.intersection(student_words)
    missing = keywords.difference(student_words)
    
    word_count = len(re.findall(r'\b\w+\b', student_answer))
    
    # Match percentage
    match_pct = len(matched) / len(keywords) if keywords else 0
    
    # Assess rating
    if word_count < 15:
        rating = "Needs Improvement"
        tip = "Your response is very short. Try to give a more comprehensive answer, explaining the background context, your actions, and the results (using the STAR method)."
    elif match_pct >= 0.5:
        rating = "Excellent"
        tip = "Fantastic response! You addressed all core parts of the question, using specific technical terms and describing your role clearly."
    elif match_pct >= 0.25:
        rating = "Good"
        tip = "Good answer. You covered several key aspects. To make it stronger, consider discussing more concrete baseline numbers, troubleshooting details, or architectural alternatives."
    else:
        rating = "Satisfactory"
        tip = "A reasonable start, but you could provide more technical depth. Make sure to describe the exact tools, metrics, or processes involved in your design."
        
    return {
        "rating": rating,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)[:5], # limit size
        "word_count": word_count,
        "tip": tip
    }

@chat_bp.route('/start', methods=['POST'])
@jwt_required()
def start_chat_session():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    analysis_id = data.get('analysis_id')

    if not analysis_id:
        return jsonify({"error": "analysis_id is required"}), 400

    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis record not found"}), 404

    # Check if there's already an active (uncompleted) session for this analysis
    session = ChatSession.query.filter_by(user_id=user_id, analysis_id=analysis_id, is_completed=False).first()
    
    if not session:
        # Create a new session
        session = ChatSession(
            user_id=user_id,
            analysis_id=analysis_id,
            current_question_index=0,
            is_completed=False
        )
        db.session.add(session)
        db.session.flush() # populate ID

        # Fetch questions
        questions = InterviewQuestion.query.filter_by(analysis_id=analysis_id).all()
        if not questions:
            return jsonify({"error": "No questions generated for this analysis. Please run analysis first."}), 400

        job = JobDescription.query.get(analysis.job_id)
        job_title = job.title if job else "the target position"

        first_q = questions[0].question
        
        # Add welcome message from interviewer
        welcome_msg = (
            f"Hello! I am your TalentForge AI Interview Coach. I've analyzed your resume and will "
            f"conduct a mock interview for the position of **{job_title}** today.\n\n"
            f"I'll ask you a series of resume-based questions to help you prepare. When you're ready, "
            f"please answer the first question below:\n\n"
            f"**Question 1:** {first_q}"
        )
        
        db_welcome = ChatMessage(
            session_id=session.id,
            sender='interviewer',
            message=welcome_msg
        )
        db.session.add(db_welcome)
        db.session.commit()
    
    # Load messages
    messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()
    
    # Get questions
    questions = InterviewQuestion.query.filter_by(analysis_id=analysis_id).all()

    return jsonify({
        "session": session.to_dict(),
        "messages": [m.to_dict() for m in messages],
        "total_questions": len(questions)
    }), 200

@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_chat_message():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    session_id = data.get('session_id')
    student_message = data.get('message', '').strip()

    if not session_id or not student_message:
        return jsonify({"error": "session_id and message are required"}), 400

    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Chat session not found"}), 404

    if session.is_completed:
        return jsonify({"error": "This interview session has already completed."}), 400

    # Fetch questions
    questions = InterviewQuestion.query.filter_by(analysis_id=session.analysis_id).all()
    if not questions:
        return jsonify({"error": "No questions associated with this session."}), 400

    # 1. Save student response
    db_student_msg = ChatMessage(
        session_id=session.id,
        sender='student',
        message=student_message
    )
    
    # 2. Evaluate current answer
    curr_idx = session.current_question_index
    if curr_idx < len(questions):
        curr_q = questions[curr_idx]
        evaluation = evaluate_answer(student_message, curr_q.answer_guideline)
        db_student_msg.set_feedback(evaluation)
        db.session.add(db_student_msg)
        
        # Increment index
        session.current_question_index += 1
        db.session.flush()
    else:
        return jsonify({"error": "Session state mismatch"}), 400

    # 3. Formulate next response from interviewer
    next_idx = session.current_question_index
    if next_idx < len(questions):
        next_q = questions[next_idx]
        interviewer_msg = (
            f"Thank you. Based on your response, here is my feedback:\n\n"
            f"* **Assessment:** {evaluation['rating']}\n"
            f"* **Strengths:** {', '.join(evaluation['matched_keywords']) if evaluation['matched_keywords'] else 'Generic response structure'}\n"
            f"* **Tip:** {evaluation['tip']}\n\n"
            f"Let's move to the next question:\n\n"
            f"**Question {next_idx + 1}:** {next_q.question}"
        )
    else:
        # All questions completed
        session.is_completed = True
        
        # Calculate overall score stats from all student messages in this session
        all_student_msgs = ChatMessage.query.filter_by(session_id=session.id, sender='student').all()
        # include the current one which is not committed yet
        ratings = [m.get_feedback()["rating"] for m in all_student_msgs if m.feedback]
        ratings.append(evaluation["rating"])
        
        excellent_cnt = ratings.count("Excellent")
        good_cnt = ratings.count("Good")
        satisfactory_cnt = ratings.count("Satisfactory")
        needs_imp_cnt = ratings.count("Needs Improvement")
        
        score_summary = (
            f"Excellent: {excellent_cnt} | Good: {good_cnt} | "
            f"Satisfactory: {satisfactory_cnt} | Needs Improvement: {needs_imp_cnt}"
        )
        
        interviewer_msg = (
            f"Thank you. Here is my feedback on your final response:\n\n"
            f"* **Assessment:** {evaluation['rating']}\n"
            f"* **Strengths:** {', '.join(evaluation['matched_keywords']) if evaluation['matched_keywords'] else 'No matching key skills'}\n"
            f"* **Tip:** {evaluation['tip']}\n\n"
            f"🎉 **Practice Interview Completed!**\n\n"
            f"Congratulations on finishing this mock interview! You've answered all {len(questions)} questions.\n\n"
            f"**Performance Summary:**\n"
            f"- {score_summary}\n\n"
            f"Feel free to select another resume or job description to start a new practice session and continue improving!"
        )

    db_interviewer_msg = ChatMessage(
        session_id=session.id,
        sender='interviewer',
        message=interviewer_msg
    )
    db.session.add(db_interviewer_msg)
    db.session.commit()

    messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        "session": session.to_dict(),
        "messages": [m.to_dict() for m in messages],
        "feedback": evaluation
    }), 200

@chat_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_chat_history(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Chat session not found"}), 404

    messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()
    questions = InterviewQuestion.query.filter_by(analysis_id=session.analysis_id).all()

    return jsonify({
        "session": session.to_dict(),
        "messages": [m.to_dict() for m in messages],
        "total_questions": len(questions)
    }), 200

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_all_sessions():
    user_id = get_jwt_identity()
    sessions = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
    
    results = []
    for s in sessions:
        analysis = Analysis.query.get(s.analysis_id)
        if not analysis:
            continue
        job = JobDescription.query.get(analysis.job_id)
        resume = Resume.query.get(analysis.resume_id)
        
        item = s.to_dict()
        item["job_title"] = job.title if job else "Unknown Role"
        item["resume_filename"] = resume.filename if resume else "Deleted Resume"
        results.append(item)

    return jsonify(results), 200
