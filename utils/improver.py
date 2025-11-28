# improver.py

from flask import Flask, render_template, session, redirect, url_for, request
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ----------------- HELPER FUNCTION -----------------
def generate_improvement_suggestions(resume_text):
    """
    Generate suggestions based on resume content
    """
    suggestions = []

    # Missing contact info
    if "@" not in resume_text:
        suggestions.append("Add a professional email address.")
    if not re.search(r'\d{10}', resume_text):
        suggestions.append("Include a phone number.")

    # Short resume
    if len(resume_text) < 300:
        suggestions.append("Add more experience or projects to your resume.")

    # Weak words
    for word in ["thing", "stuff", "bad", "etc"]:
        if word in resume_text.lower():
            suggestions.append(f"Replace the word '{word}' with stronger terminology.")

    # Keywords
    keywords = ["python", "sql", "excel", "ml", "communication",
                "leadership", "project", "api", "cloud", "teamwork", "management"]
    for kw in keywords:
        if kw.lower() not in resume_text.lower():
            suggestions.append(f"Consider adding the keyword '{kw}' if relevant.")

    return suggestions

# ----------------- ROUTE -----------------
@app.route("/improved_resume")
def improved_resume():
    resume_text = session.get('resume_text')
    if not resume_text:
        return redirect(url_for('home')) 

    improvement_suggestions = generate_improvement_suggestions(resume_text)

    return render_template("improved_resume.html", suggestions=improvement_suggestions)
