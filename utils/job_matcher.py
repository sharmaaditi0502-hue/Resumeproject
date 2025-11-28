
import re


JOB_DATABASE = [
    {
        "title": "Data Analyst",
        "company": "TechCorp",
        "keywords": ["python", "sql", "excel", "data analysis", "reporting"]
    },
    {
        "title": "Software Engineer",
        "company": "InnovateX",
        "keywords": ["java", "c++", "python", "git", "api"]
    },
    {
        "title": "Project Manager",
        "company": "ManageIt",
        "keywords": ["leadership", "teamwork", "communication", "planning", "project"]
    },
]


KEYWORD_SUGGESTIONS = {
    "python": ["Projects using Python", "Python certifications"],
    "sql": ["SQL projects", "Database querying skills"],
    "excel": ["Advanced Excel skills", "Pivot tables experience"],
    "leadership": ["Led team projects", "Managed team of X members"],
    "communication": ["Excellent verbal/written communication", "Client interaction experience"],
    "project": ["Include project descriptions with outcomes"],
    "data analysis": ["Include data analysis projects or reports"],
    "api": ["Show experience with APIs or integration projects"]
}

def match_jobs(resume_text):
    """
    Match resume against jobs and return structured data
    including match_score, missing_keywords, and actionable suggestions.
    """
    resume_text_lower = resume_text.lower()
    matched_jobs = []

    for job in JOB_DATABASE:
        job_keywords = job["keywords"]
        matched = [kw for kw in job_keywords if re.search(r'\b' + re.escape(kw) + r'\b', resume_text_lower)]
        missing = [kw for kw in job_keywords if kw not in matched]
        
        match_score = int(len(matched) / len(job_keywords) * 100) if job_keywords else 0

        
        suggestions = []
        for kw in missing:
            if kw in KEYWORD_SUGGESTIONS:
                suggestions.extend(KEYWORD_SUGGESTIONS[kw])
            else:
                suggestions.append(f"Consider adding relevant experience for '{kw}'")

        matched_jobs.append({
            "title": job["title"],
            "company": job["company"],
            "match_score": match_score,
            "missing_keywords": missing,
            "suggestions": suggestions
        })

   
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_jobs
