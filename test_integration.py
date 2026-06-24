import requests
import json
import os

BASE_URL = "http://localhost:5000/api"

def test_full_integration():
    print("--- Starting End-to-End REST API Integration Test ---")
    
    # 1. Register User
    register_url = f"{BASE_URL}/auth/register"
    reg_payload = {
        "username": "alice_integration",
        "email": "alice_integration@example.com",
        "password": "password123"
    }
    
    reg_response = requests.post(register_url, json=reg_payload)
    print(f"1. Registration Status: {reg_response.status_code}")
    if reg_response.status_code == 400 and "already exists" in reg_response.json().get("error", ""):
        print("   User already exists, continuing to login...")
    else:
        assert reg_response.status_code in [201, 200], f"Registration failed: {reg_response.text}"

    # 2. Login User
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": "alice_integration@example.com",
        "password": "password123"
    }
    login_response = requests.post(login_url, json=login_payload)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    user_id = login_response.json()["user"]["id"]
    print(f"2. Login Successful. JWT Token obtained. User ID: {user_id}")

    # Set up authorization header
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Upload Resume
    upload_url = f"{BASE_URL}/resumes/upload"
    resume_path = "mock_resume.pdf"
    assert os.path.exists(resume_path), "mock_resume.pdf does not exist. Run create_mock_resume.py first."
    
    with open(resume_path, "rb") as f:
        files = {"file": (resume_path, f, "application/pdf")}
        upload_response = requests.post(upload_url, headers=headers, files=files)
        
    assert upload_response.status_code == 201, f"Resume upload failed: {upload_response.text}"
    resume_id = upload_response.json()["resume"]["id"]
    print(f"3. Resume Upload & Parsing Successful. Resume ID: {resume_id}")

    # 4. Analyze Resume against Job Description
    analyze_url = f"{BASE_URL}/analysis/analyze"
    job_payload = {
        "resume_id": resume_id,
        "job_title": "Full-Stack Software Engineer",
        "job_description": "Seeking a developer skilled in Python, Flask, React, and SQL database storage. Experience with Docker and AWS is preferred."
    }
    analyze_response = requests.post(analyze_url, headers=headers, json=job_payload)
    assert analyze_response.status_code == 201, f"Analysis failed: {analyze_response.text}"
    analysis_data = analyze_response.json()
    analysis_id = analysis_data["analysis"]["id"]
    ats_score = analysis_data["analysis"]["ats_score"]
    print(f"4. ATS Analysis Successful. Score: {ats_score}%. Analysis ID: {analysis_id}")
    
    # 5. Fetch Dashboard Stats
    stats_url = f"{BASE_URL}/dashboard/stats"
    stats_response = requests.get(stats_url, headers=headers)
    assert stats_response.status_code == 200, f"Failed to fetch stats: {stats_response.text}"
    stats_data = stats_response.json()
    print(f"5. Dashboard Stats: Resumes={stats_data['total_resumes']}, Analyses={stats_data['total_analyses']}, Avg Score={stats_data['average_ats_score']}%")

    # 6. Download PDF Report
    report_url = f"{BASE_URL}/analysis/{analysis_id}/report"
    report_response = requests.get(report_url, headers=headers)
    assert report_response.status_code == 200, f"Report download failed: {report_response.text}"
    pdf_size = len(report_response.content)
    print(f"6. Report PDF Generated & Downloaded: {pdf_size} bytes")

    print("\n--- All End-to-End REST API Integration Tests Passed! ---")

if __name__ == "__main__":
    test_full_integration()
