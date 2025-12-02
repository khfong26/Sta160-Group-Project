from flask import Flask, render_template, jsonify, request
import os
import sys
import pandas as pd
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from api.data_loader import load_all_states_data
from src.analysis.recommendation_model import recommend_jobs, extract_resume_text


app = Flask(__name__)

# front end

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/salary")
def salary_page():
    return render_template("salary.html")

@app.route("/skills")
def skills_page():
    return render_template("skills.html")

@app.route("/trends")
def trends_page():
    return render_template("trends.html")

@app.route("/methodology")
def methodology_page():
    return render_template("methodology.html")

@app.route("/team")
def team_page():
    return render_template("team.html")

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "POST":
        resume_file = request.files.get("resume")

        if not resume_file:
            return render_template("recommend.html", results=None, error="No file uploaded")

        # Convert uploaded resume to text (PDF or TXT)
        try:
            resume_text = extract_resume_text(resume_file)
        except Exception as e:
            return render_template("recommend.html", results=None, error=f"Could not read resume: {e}")

        # Run recommendation model
        df_results = recommend_jobs(resume_text)

        # Only keep columns you want to show users
        keep_cols = ["title", "company", "location", "description", "job_url", "final_score"]
        df_results = df_results[[c for c in keep_cols if c in df_results.columns]]

        results = df_results.to_dict(orient="records")

        return render_template("recommend.html", results=results, error=None)

    return render_template("recommend.html", results=None, error=None)




# API Routes (JSON Data for Charts)

@app.route("/api/salary")
def salary_api():
    df = load_all_states_data()
    
    # Filters
    location = request.args.get('location')
    job = request.args.get('job')
    
    if location and location != "All locations":
        if location == "Remote":
            # Check both location string and is_remote flag
            df = df[
                (df['location'].str.contains("Remote", case=False, na=False)) | 
                (df['is_remote'] == True) | 
                (df['is_remote'] == "True")
            ]
        else:
            df = df[df['location'].str.contains(location, case=False, na=False)]
            
    if job and job != "All jobs":
        df = df[df['title'].str.contains(job, case=False, na=False)]
        
    # Calculate average salary
    # Ensure numeric
    df['min_amount'] = pd.to_numeric(df['min_amount'], errors='coerce')
    df['max_amount'] = pd.to_numeric(df['max_amount'], errors='coerce')
    df = df.dropna(subset=['min_amount', 'max_amount'])
    
    # Calculate average for each row
    df['avg_salary'] = (df['min_amount'] + df['max_amount']) / 2
    
    return jsonify({'salary': df['avg_salary'].tolist()})

@app.route("/api/skills")
def skills_api():
    df = load_all_states_data()
    
    # Extract skills
    all_skills = []
    for skills_str in df['parsed_skills'].dropna():
        # Assuming comma separated
        skills = [s.strip() for s in skills_str.split(',')]
        all_skills.extend(skills)
        
    counts = Counter(all_skills)
    most_common = counts.most_common(20) # Top 20
    
    return jsonify({
        'skill': [x[0] for x in most_common],
        'count': [x[1] for x in most_common]
    })

@app.route("/api/trends")
def trends_api():
    df = load_all_states_data()

    # Filters
    location = request.args.get('location')
    job = request.args.get('job')
    
    if location and location != "All locations":
        if location == "Remote":
            df = df[
                (df['location'].str.contains("Remote", case=False, na=False)) | 
                (df['is_remote'] == True) | 
                (df['is_remote'] == "True")
            ]
        else:
            df = df[df['location'].str.contains(location, case=False, na=False)]
            
    if job and job != "All jobs":
        df = df[df['title'].str.contains(job, case=False, na=False)]
    
    # Ensure date
    df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
    df = df.dropna(subset=['date_posted'])
    
    daily_counts = df.groupby('date_posted').size().reset_index(name='postings')
    daily_counts = daily_counts.sort_values('date_posted')
    
    return jsonify({
        'date': daily_counts['date_posted'].dt.strftime('%Y-%m-%d').tolist(),
        'postings': daily_counts['postings'].tolist()
    })


if __name__ == "__main__":
    app.run(debug=True)
