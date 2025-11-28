import re
import pdfplumber
from docx import Document

# ----------------- EXTRACT TEXT -----------------
def extract_text_from_file(file):
    ext = file.filename.split('.')[-1].lower()
    if ext == "pdf":
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        return text
    elif ext == "docx":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return "Unsupported file"

# ----------------- CALCULATE ATS SCORE -----------------
def calculate_ats_score(resume_text):
    keywords = ["python", "sql", "excel", "ml", "communication",
                "leadership", "project", "api", "cloud", "teamwork", "management"]
    resume_lower = resume_text.lower()
    matched = [kw for kw in keywords if kw.lower() in resume_lower]
    missing = [kw for kw in keywords if kw.lower() not in resume_lower]

    base_score = 40
    length_score = min(len(resume_text)//50, 30)
    keyword_score = int((len(matched)/len(keywords))*30)

    ats_score = base_score + length_score + keyword_score
    ats_score = min(ats_score, 100)
    return ats_score, matched, missing

# ----------------- GENERATE ATS HTML -----------------
def generate_ats_html(resume_text):
    ats_score, matched, missing = calculate_ats_score(resume_text)

    highlights = []
    if "improved" in resume_text.lower(): highlights.append("Shows measurable achievements")
    if "led" in resume_text.lower(): highlights.append("Leadership experience found")
    if "project" in resume_text.lower(): highlights.append("Good project details included")
    if "team" in resume_text.lower(): highlights.append("Teamwork emphasized")
    if "managed" in resume_text.lower(): highlights.append("Management experience highlighted")

    weak_words = []
    for word in ["thing", "stuff", "bad", "etc"]:
        if word in resume_text.lower():
            weak_words.append(word)

    suggestions = [
        "Add more role-specific keywords",
        "Quantify achievements",
        "Use strong action verbs",
        "Improve formatting for ATS readability"
    ]

    # Dynamic scores for bars
    total_keywords = len(matched) + len(missing)
    keyword_percent = int((len(matched)/total_keywords)*100) if total_keywords else 0
    length_percent = min(len(resume_text)//5, 100)
    action_percent = 50 + min(len(highlights)*10, 50)

    html = f"""
    <html>
    <head>
        <title>ATS Score Report</title>
        <style>
            body {{ font-family: Arial; background:#fdf6f0; color:#5a4a3c; padding:20px; }}
            .container {{ max-width:900px; margin:auto; background:white; padding:30px; border-radius:12px; box-shadow:0 5px 25px rgba(0,0,0,0.15); }}
            h1 {{ text-align:center; color:#6f4e37; font-size:35px; }}
            .score-box {{ margin:20px 0; }}
            .score-label {{ font-weight:bold; margin-bottom:6px; }}
            .score-bar {{ background:#e0e0e0; border-radius:25px; overflow:hidden; height:25px; }}
            .score-fill {{ background:#6f4e37; height:100%; width:0; line-height:25px; color:white; text-align:right; padding-right:10px; border-radius:25px; transition: width 1s ease-in-out; }}
            .section {{ margin-top:25px; }}
            .flex-container {{ display:flex; gap:20px; flex-wrap:wrap; justify-content:center; }}
            .flex-box {{ background:#fefefe; padding:20px; border-radius:10px; flex:1 1 250px; box-shadow:0 5px 15px rgba(0,0,0,0.1); }}
            .flex-box h4 {{ margin-bottom:10px; color:#6f4e37; }}
            .improve-btn {{ display:block; margin:25px auto; text-align:center; background:#6f4e37; color:white; padding:12px 20px; text-decoration:none; border-radius:8px; font-weight:bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ATS Score Report</h1>

            <div class="score-box">
                <div class="score-label">Overall ATS Score</div>
                <div class="score-bar">
                    <div class="score-fill" id="overall-score">{ats_score}%</div>
                </div>
            </div>
            <div class="score-box">
                <div class="score-label">Keyword Optimization</div>
                <div class="score-bar">
                    <div class="score-fill" id="keyword-bar">{keyword_percent}%</div>
                </div>
            </div>
            <div class="score-box">
                <div class="score-label">Resume Length</div>
                <div class="score-bar">
                    <div class="score-fill" id="length-bar">{length_percent}%</div>
                </div>
            </div>
            <div class="score-box">
                <div class="score-label">Action Verbs Usage</div>
                <div class="score-bar">
                    <div class="score-fill" id="action-bar">{action_percent}%</div>
                </div>
            </div>

            <div class="section flex-container">
                <div class="flex-box">
                    <h4>Matched Keywords</h4>
                    <ul>{''.join(f"<li>{w}</li>" for w in matched)}</ul>
                </div>
                <div class="flex-box">
                    <h4>Missing Keywords</h4>
                    <ul>{''.join(f"<li>{w}</li>" for w in missing)}</ul>
                </div>
            </div>

            <div class="section flex-container">
                <div class="flex-box">
                    <h4>Highlights</h4>
                    <ul>{''.join(f"<li>{h}</li>" for h in highlights)}</ul>
                </div>
                <div class="flex-box">
                    <h4>Weak Words</h4>
                    <ul>{''.join(f"<li>{w}</li>" for w in weak_words)}</ul>
                </div>
            </div>

            <div class="section">
                <h3>Suggestions</h3>
                <ul>{''.join(f"<li>{s}</li>" for s in suggestions)}</ul>
            </div>

            <a href="/improved_resume" class="improve-btn">Improve Resume</a>
        </div>

        <script>
            function animateBar(id, value) {{
                const bar = document.getElementById(id);
                let width = 0;
                const interval = setInterval(() => {{
                    if(width >= value) clearInterval(interval);
                    bar.style.width = width + "%";
                    width++;
                }}, 10);
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                animateBar("overall-score", {ats_score});
                animateBar("keyword-bar", {keyword_percent});
                animateBar("length-bar", {length_percent});
                animateBar("action-bar", {action_percent});
            }});
        </script>
    </body>
    </html>
    """
    return html

# ----------------- IMPROVEMENT SUGGESTIONS -----------------
def generate_improvement_suggestions(resume_text):
    suggestions = []
    if "@" not in resume_text:
        suggestions.append("Add a professional email address.")
    if not re.search(r'\d{10}', resume_text):
        suggestions.append("Include a phone number.")
    if len(resume_text) < 300:
        suggestions.append("Add more experience or projects to your resume.")
    for word in ["thing", "stuff", "bad", "etc"]:
        if word in resume_text.lower():
            suggestions.append(f"Replace the word '{word}' with stronger terminology.")
    keywords = ["python", "sql", "excel", "ml", "communication",
                "leadership", "project", "api", "cloud", "teamwork", "management"]
    for kw in keywords:
        if kw.lower() not in resume_text.lower():
            suggestions.append(f"Consider adding the keyword '{kw}' if relevant.")
    return suggestions
