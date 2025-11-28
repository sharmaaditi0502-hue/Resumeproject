from flask import Flask, render_template, request, redirect, url_for, session
import os
import re
from utils.ats_score import extract_text_from_file, generate_ats_html
from utils.job_matcher import match_jobs
from utils.ats_score import extract_text_from_file, calculate_ats_score, generate_improvement_suggestions
app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ---------------- HELPERS ----------------

TECH_SKILLS = [
    "python", "sql", "excel", "ml", "api", "cloud", "java", "javascript", 
    "docker", "aws", "c++", "html", "css", "react", "node"
]
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "management", "problem solving",
    "collaboration", "adaptability", "creativity"
]
ACTION_VERBS = ["developed", "designed", "led", "implemented", "created", "managed", "coordinated"]
WEAK_WORDS = ["responsible for", "worked on", "helped", "participated in", "thing", "stuff", "etc"]

SECTION_HEADERS = ["summary", "experience", "education", "skills", "projects", "certifications"]

# ---------------- Keyword / Text Analysis ----------------

def extract_keywords(text):
    all_skills = TECH_SKILLS + SOFT_SKILLS
    found = [kw for kw in all_skills if re.search(r'\b' + re.escape(kw) + r'\b', text, re.I)]
    return found

def missing_keywords(text):
    found = extract_keywords(text)
    missing = [kw for kw in TECH_SKILLS + SOFT_SKILLS if kw not in found]
    return missing

def detect_weak_words(text):
    return [w for w in WEAK_WORDS if w.lower() in text.lower()]

def extract_highlights(text):
    highlights = []

    # Detect measurable achievements
    nums = re.findall(r'\d+%?|\$\d+', text)
    if nums:
        highlights.append(f"Measurable achievements detected: {', '.join(nums)}")

    # Detect leadership phrases
    leadership_words = ["led", "managed", "supervised", "coordinated", "head of"]
    for word in leadership_words:
        if word.lower() in text.lower():
            highlights.append(f"Leadership experience via '{word}'")

    # Projects
    if "project" in text.lower():
        highlights.append("Project involvement detected")

    # Skills detected
    skills_found = extract_keywords(text)
    if skills_found:
        highlights.append(f"Skills detected: {', '.join(skills_found)}")

    # Action verbs
    actions_found = [av for av in ACTION_VERBS if av in text.lower()]
    if actions_found:
        highlights.append(f"Action verbs used: {', '.join(actions_found)}")

    return highlights

def generate_suggestions(text):
    suggestions = []

    # Missing keywords
    missing = missing_keywords(text)
    if missing:
        suggestions.append(f"Include relevant keywords: {', '.join(missing)}")

    # Weak words
    weak = detect_weak_words(text)
    if weak:
        suggestions.append(f"Replace weak words: {', '.join(weak)}")

    # Action verbs
    if not any(av in text.lower() for av in ACTION_VERBS):
        suggestions.append("Use strong action verbs like: developed, led, implemented, created.")

    # Section advice
    for section in SECTION_HEADERS:
        if section not in text.lower():
            suggestions.append(f"Add '{section.title()}' section for better structure.")

    return suggestions

# ---------------- Score Calculations ----------------

def calculate_keyword_score(text):
    keywords = TECH_SKILLS + SOFT_SKILLS
    found = extract_keywords(text)
    return int(len(found) / len(keywords) * 100) if keywords else 0

def calculate_structure_score(text):
    total_sections = len(SECTION_HEADERS)
    present_sections = sum(1 for s in SECTION_HEADERS if s in text.lower())
    return int(present_sections / total_sections * 100)

def calculate_action_score(text):
    total_actions = len(ACTION_VERBS)
    present_actions = sum(1 for a in ACTION_VERBS if a in text.lower())
    return int(present_actions / total_actions * 100) if total_actions else 0

def calculate_formatting_score(text):
    score = 0
    if re.search(r'•|-|\*', text):
        score += 40
    if any(h in text.lower() for h in SECTION_HEADERS):
        score += 30
    if "\n\n" in text or "\n" in text:
        score += 30
    return min(score, 100)

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analysis", methods=["POST"])
def analysis():
    file = request.files.get("resume")
    if not file or file.filename == "":
        return "Please upload a valid resume file", 400

    resume_text = extract_text_from_file(file)
    session["resume_text"] = resume_text
    session["resume_file"] = file.filename

    matched_keywords = extract_keywords(resume_text)
    missing_keywords_list = missing_keywords(resume_text)
    weak_words_list = detect_weak_words(resume_text)
    highlights_list = extract_highlights(resume_text)
    suggestions_list = generate_suggestions(resume_text)

    # Scores
    keyword_score = calculate_keyword_score(resume_text)
    resume_score = int((keyword_score + calculate_structure_score(resume_text) + calculate_action_score(resume_text) + calculate_formatting_score(resume_text)) / 4)

    sequence_feedback = "Improve section ordering for better ATS readability."
    issues = missing_keywords_list + weak_words_list

    return render_template(
        "analysis.html",
        score=resume_score,
        keyword_score=keyword_score,
        issues=issues,
        wrong_words=weak_words_list,
        highlights=highlights_list,
        suggestions=suggestions_list,
        sequence_feedback=sequence_feedback,
        missing_keywords=missing_keywords_list
    )

@app.route("/improved_resume")
def improved_resume():
    resume_text = session.get('resume_text')
    if not resume_text:
        return redirect(url_for('home'))

    # Actual ATS score & keywords
    ats_score, matched_keywords, missing_keywords = calculate_ats_score(resume_text)

    # Actual improvement suggestions
    improvement_suggestions = generate_improvement_suggestions(resume_text)

    # Highlights based on resume content
    highlights = []
    if "improved" in resume_text.lower():
        highlights.append("Shows measurable achievements")
    if "led" in resume_text.lower():
        highlights.append("Leadership experience found")
    if "project" in resume_text.lower():
        highlights.append("Good project details included")
    if "team" in resume_text.lower():
        highlights.append("Teamwork emphasized")
    if "managed" in resume_text.lower():
        highlights.append("Management experience highlighted")

    # Calculate dynamic scores for bars
    total_keywords = len(matched_keywords) + len(missing_keywords)
    keyword_score = int((len(matched_keywords)/total_keywords)*100) if total_keywords > 0 else 0

    structure_score = min(len(resume_text)//50, 100)

    action_verbs = ["led", "managed", "developed", "designed", "improved", "created", "implemented"]
    action_score = sum(10 for w in action_verbs if w in resume_text.lower())
    action_score = min(action_score, 100)

    formatting_score = 90  # Optional: could calculate actual formatting quality

    return render_template(
        "improved_resume.html",
        keyword_score=keyword_score,
        structure_score=structure_score,
        action_score=action_score,
        formatting_score=formatting_score,
        highlights=highlights,
        suggestions=improvement_suggestions,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords
    )

@app.route("/ats-score")
def ats_score_page():
    resume_text = session.get("resume_text")
    if not resume_text:
        return "No resume found. Please upload your resume first.", 400

    html = generate_ats_html(resume_text)
    return html
@app.route("/job_suggestions")
def job_suggestions():
    resume_text = session.get("resume_text")
    if not resume_text:
        return redirect(url_for("home"))

    matched_jobs = match_jobs(resume_text)
   
    resume_highlights = extract_highlights(resume_text)

    return render_template(
        "job_suggestions.html",
        jobs=matched_jobs,
        resume_highlights=resume_highlights
    )
@app.route("/final_report")
def final_report():
    resume_text = session.get("resume_text")
    if not resume_text:
        return redirect(url_for("home"))

    # Extract all data
    found_keywords = extract_keywords(resume_text)
    missing_keywords_list = missing_keywords(resume_text)
    weak_words_list = detect_weak_words(resume_text)
    highlights_list = extract_highlights(resume_text)
    suggestions_list = generate_suggestions(resume_text)

    keyword_score = int(len(found_keywords) / (len(found_keywords) + len(missing_keywords_list)) * 100 if (found_keywords + missing_keywords_list) else 0)
    
    # Additional metrics (dummy example scores, can compute based on logic)
    ats_score = 80  # Example: could be calculated from ATS parsing rules
    content_quality = 75
    experience_evolution = 70
    skills_gap = len(missing_keywords_list)
    achievement_quality = 85
    formatting_layout = 80
    summary_eval = 70
    job_match_score = 78
    duplicate_info = ["worked on", "responsible for"]
    gap_red_flags = ["missing contact info", "missing summary"]
    section_check = {"Experience": True, "Education": True, "Skills": True, "Projects": False}
    
    return render_template(
        "final_report.html",
        found_keywords=found_keywords,
        missing_keywords=missing_keywords_list,
        weak_words=weak_words_list,
        highlights=highlights_list,
        suggestions=suggestions_list,
        keyword_score=keyword_score,
        ats_score=ats_score,
        content_quality=content_quality,
        experience_evolution=experience_evolution,
        skills_gap=skills_gap,
        achievement_quality=achievement_quality,
        formatting_layout=formatting_layout,
        summary_eval=summary_eval,
        job_match_score=job_match_score,
        duplicate_info=duplicate_info,
        gap_red_flags=gap_red_flags,
        section_check=section_check
    )


if __name__ == "__main__":
    app.run(debug=True)
