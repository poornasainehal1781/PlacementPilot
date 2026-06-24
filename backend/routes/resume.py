import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from backend.database import db, Resume
from backend.parser import parse_resume

resume_bp = Blueprint('resume', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@resume_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Only PDF and DOCX are allowed."}), 400

    try:
        filename = secure_filename(file.filename)
        # Create a unique filename prefixing user id to prevent conflicts
        unique_filename = f"user_{user_id}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Parse the resume file
        parsed_data = parse_resume(filepath)

        # Store in database
        new_resume = Resume(
            user_id=user_id,
            filename=filename,
            raw_text=parsed_data["raw_text"]
        )
        new_resume.set_skills(parsed_data["skills"])
        new_resume.set_experience(parsed_data["experience"])
        new_resume.set_education(parsed_data["education"])

        db.session.add(new_resume)
        db.session.commit()

        # Keep the file saved but return parsed info
        return jsonify({
            "message": "Resume uploaded and parsed successfully",
            "resume": new_resume.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to upload and parse resume: {str(e)}"}), 500

@resume_bp.route('/', methods=['GET'])
@jwt_required()
def get_resumes():
    user_id = get_jwt_identity()
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
    return jsonify([r.to_dict() for r in resumes]), 200

@resume_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    return jsonify(resume.to_dict()), 200

@resume_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    try:
        # Optionally remove the physical file if wanted
        # We can construct filename and delete, but leaving it or deleting is fine.
        db.session.delete(resume)
        db.session.commit()
        return jsonify({"message": "Resume deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete resume: {str(e)}"}), 500
