import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom simple styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    story = []
    
    story.append(Paragraph("Alice Smith", title_style))
    story.append(Paragraph("Email: alice.smith@example.com | Phone: 555-019-2831", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", styles['Heading3']))
    story.append(Paragraph("Python, Javascript, React, SQL, Flask, Git, Docker, HTML, CSS", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>WORK EXPERIENCE</b>", styles['Heading3']))
    story.append(Paragraph("<b>Full Stack Developer</b> - WebTech (2021 - Present)", body_style))
    story.append(Paragraph("Developed web applications using React, Python, and Flask. Optimized database queries using SQL.", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>EDUCATION</b>", styles['Heading3']))
    story.append(Paragraph("B.S. in Computer Science - Tech University (2017 - 2021)", body_style))
    
    doc.build(story)
    print(f"Created PDF resume at {filename}")

if __name__ == '__main__':
    create_pdf("mock_resume.pdf")
