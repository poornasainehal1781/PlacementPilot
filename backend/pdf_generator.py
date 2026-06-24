import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(analysis, resume, job, questions, output_path):
    """
    Generates a beautifully formatted PDF report of the ATS analysis.
    """
    # Setup document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles to avoid modifying defaults directly
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#312E81") # Indigo-900
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4B5563") # Gray-600
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1E1B4B"), # Indigo-950
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1F2937") # Gray-800
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1F2937"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )

    header_table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEF2F6")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ])

    story = []

    # Title & Header
    title_p = Paragraph("ATS RESUME ANALYSIS REPORT", title_style)
    date_str = datetime.now().strftime("%B %d, %Y")
    subtitle_p = Paragraph(f"Generated on: {date_str} | Role: {job.title}", subtitle_style)
    
    story.append(title_p)
    story.append(subtitle_p)
    story.append(Spacer(1, 15))
    
    # Candidate details & ATS Score Summary
    name = resume.get_skills() # wait, resume.name or parsed_name
    # Let's get parsed name and email
    resume_skills = resume.get_skills()
    
    # Let's create candidate summary panel
    import json
    # Let's read properties directly
    parsed_skills = resume.get_skills()
    
    cand_info = f"<b>Candidate:</b> {resume.filename}<br/>"
    cand_info += f"<b>Total Skills Extracted:</b> {len(parsed_skills)}<br/>"
    
    # Add email/phone from parse if available (we will store in raw_json or retrieve)
    # Since we store in resume.raw_text, let's just use placeholder metadata or parse it
    
    score_color = "#10B981" # Green
    if analysis.ats_score < 50:
        score_color = "#EF4444" # Red
    elif analysis.ats_score < 80:
        score_color = "#F59E0B" # Orange

    score_html = f"<font size=14><b>ATS Score:</b></font><br/><font size=32 color='{score_color}'><b>{analysis.ats_score}%</b></font>"
    
    header_data = [
        [Paragraph(cand_info, body_style), Paragraph(score_html, body_style)]
    ]
    header_table = Table(header_data, colWidths=[4.0*inch, 3.0*inch])
    header_table.setStyle(header_table_style)
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # Recommendations
    story.append(Paragraph("General Assessment", h1_style))
    recs = analysis.get_recommendations()
    feedback = recs.get("general_feedback", "No feedback available.")
    story.append(Paragraph(feedback, body_style))
    story.append(Spacer(1, 10))

    # Formatting and structural feedback
    formatting_sugs = recs.get("formatting_suggestions", [])
    if formatting_sugs:
        story.append(Paragraph("Formatting & Structural Recommendations", h1_style))
        for sug in formatting_sugs:
            story.append(Paragraph(f"• {sug}", bullet_style))
        story.append(Spacer(1, 10))
        
    # Skills match Table
    story.append(Paragraph("Skills & Keyword Matching Analysis", h1_style))
    
    matched_skills = analysis.get_missing_skills() # wait, let's verify names
    # Let's pull match and missing skills
    import json
    # For safe extraction
    try:
        matched_skills_list = json.loads(analysis.missing_skills) # Wait, let's verify in database.py
    except:
        matched_skills_list = []
        
    # Let's read directly from record
    missing_skills_list = analysis.get_missing_skills()
    # Let's retrieve matched skills
    # Since we only stored missing_skills in Analysis model, let's compute matched skills dynamically
    # or get it if it's there.
    all_jd_skills = job.get_skills()
    matched_skills_list = [s for s in all_jd_skills if s not in missing_skills_list]

    matched_text = ", ".join(matched_skills_list) if matched_skills_list else "None detected"
    missing_text = ", ".join(missing_skills_list) if missing_skills_list else "None! Excellent job!"
    
    skills_data = [
        [Paragraph("<b>Matched Skills</b>", body_style), Paragraph("<b>Missing Skills (Crucial Gaps)</b>", body_style)],
        [Paragraph(matched_text, body_style), Paragraph(missing_text, body_style)]
    ]
    skills_table = Table(skills_data, colWidths=[3.5*inch, 3.5*inch])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#312E81")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    
    # Force white text for table header using paragraph formatting or direct text
    skills_data[0][0] = Paragraph("<font color='white'><b>Matched Skills</b></font>", body_style)
    skills_data[0][1] = Paragraph("<font color='white'><b>Missing Skills (Crucial Gaps)</b></font>", body_style)
    skills_table = Table(skills_data, colWidths=[3.5*inch, 3.5*inch])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#312E81")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))
    
    # Actionable Resume Improvements
    actionable_improvements = recs.get("actionable_improvements", [])
    if actionable_improvements:
        story.append(Paragraph("Actionable Resume Improvements (Where, What & How)", h1_style))
        
        # Table columns: Where to Change, What to Change, Action Strategy
        imp_headers = [
            Paragraph("<font color='white'><b>Section / Location</b></font>", body_style),
            Paragraph("<font color='white'><b>What to Change</b></font>", body_style),
            Paragraph("<font color='white'><b>Action Strategy / How-To</b></font>", body_style)
        ]
        
        imp_rows = [imp_headers]
        for imp in actionable_improvements:
            imp_rows.append([
                Paragraph(f"<b>{imp.get('where', 'N/A')}</b>", body_style),
                Paragraph(imp.get('what', 'N/A'), body_style),
                Paragraph(imp.get('how', 'N/A'), body_style)
            ])
            
        imp_table = Table(imp_rows, colWidths=[1.8*inch, 2.2*inch, 3.0*inch])
        imp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F46E5")), # Indigo-600
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]), # alternating background
        ]))
        story.append(imp_table)
        story.append(Spacer(1, 15))
        
    # Page Break for Interview Prep Section
    story.append(PageBreak())
    
    # Interview Preparation Questions
    story.append(Paragraph("Tailored Interview Preparation Questions", h1_style))
    story.append(Paragraph("Below are generated interview questions based on your resume profile and the job requirements, along with recommended talking points.", body_style))
    story.append(Spacer(1, 10))
    
    for idx, q in enumerate(questions, 1):
        q_elements = []
        q_elements.append(Paragraph(f"<b>Q{idx}: {q.question}</b>", ParagraphStyle('QStyle', parent=body_style, fontName='Helvetica-Bold', fontSize=10, leading=14, spaceBefore=8)))
        q_elements.append(Paragraph(f"<i>Type: {q.question_type}</i>", ParagraphStyle('QTypeStyle', parent=body_style, fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#4B5563"))))
        q_elements.append(Spacer(1, 4))
        q_elements.append(Paragraph(f"<b>Suggested Answer Strategy:</b> {q.answer_guideline}", ParagraphStyle('AStyle', parent=body_style, leftIndent=10)))
        q_elements.append(Spacer(1, 8))
        
        # Keep each question and its answer guideline on the same page if possible
        story.append(KeepTogether(q_elements))
        
    doc.build(story)
