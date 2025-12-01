from flask import Flask, render_template, jsonify, request
import os
import sys
import pandas as pd
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from api.data_loader import load_all_jobs_combined

app = Flask(__name__)

# Front end routes

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


# API Routes (JSON Data for Charts)

@app.route("/api/salary")
def salary_api():
    """API endpoint for salary data - Data Analyst and Business Analyst only."""
    # Load YOUR job data only
    df = load_all_jobs_combined()
    
    if df.empty:
        print("No data loaded in salary_api")
        return jsonify({'salary': []})
    
    print(f"Loaded {len(df)} jobs for salary analysis")
    
    # Get filters from request
    location = request.args.get('location')
    job = request.args.get('job')
    job_category = request.args.get('job_category')
    
    # Apply job category filter
    if job_category and job_category not in ["All", None, ""]:
        df = df[df['job_category'] == job_category]
        print(f"After job_category filter: {len(df)} jobs")
    
    # Apply location filter
    if location and location not in ["All locations", None, ""]:
        if location == "Remote":
            df = df[
                (df['location'].str.contains("Remote", case=False, na=False)) | 
                (df['is_remote'] == True) |
                (df['is_remote'] == "True")
            ]
        elif location == "California":
            df = df[df['state'] == 'California']
        elif location == "New York":
            df = df[df['state'] == 'New York']
        elif location == "Texas":
            df = df[df['state'] == 'Texas']
        print(f"After location filter: {len(df)} jobs")
    
    # Apply job title filter
    if job and job not in ["All jobs", None, ""]:
        df = df[df['title'].str.contains(job, case=False, na=False)]
        print(f"After job title filter: {len(df)} jobs")
    
    # Calculate average salary
    df['min_amount'] = pd.to_numeric(df['min_amount'], errors='coerce')
    df['max_amount'] = pd.to_numeric(df['max_amount'], errors='coerce')
    df = df.dropna(subset=['min_amount', 'max_amount'])
    
    if df.empty:
        print("No salary data after filtering")
        return jsonify({'salary': []})
    
    df['avg_salary'] = (df['min_amount'] + df['max_amount']) / 2
    
    print(f"Returning {len(df)} salary values")
    return jsonify({
        'salary': df['avg_salary'].tolist()
    })


@app.route("/api/skills")
def skills_api():
    """API endpoint for skills data - Data Analyst and Business Analyst only."""
    df = load_all_jobs_combined()
    
    if df.empty:
        print("No data loaded in skills_api")
        return jsonify({'skill': [], 'count': []})
    
    print(f"Loaded {len(df)} jobs for skills analysis")
    
    # Filter by job category if provided
    job_category = request.args.get('job_category')
    if job_category and job_category not in ["All", None, ""]:
        df = df[df['job_category'] == job_category]
        print(f"After job_category filter: {len(df)} jobs")
    
    # Extract skills from parsed_skills column
    all_skills = []
    for skills_str in df['parsed_skills'].dropna():
        if pd.notna(skills_str) and str(skills_str).strip():
            skills = [s.strip() for s in str(skills_str).split(',')]
            all_skills.extend(skills)
    
    if not all_skills:
        print("No skills found")
        return jsonify({'skill': [], 'count': []})
    
    # Count skills and get top 20
    counts = Counter(all_skills)
    most_common = counts.most_common(20)
    
    print(f"Returning {len(most_common)} top skills")
    return jsonify({
        'skill': [x[0] for x in most_common],
        'count': [x[1] for x in most_common]
    })


@app.route("/api/trends")
def trends_api():
    """API endpoint for job posting trends - Data Analyst and Business Analyst only."""
    df = load_all_jobs_combined()
    
    if df.empty:
        print("No data loaded in trends_api")
        return jsonify({'date': [], 'postings': []})
    
    print(f"Loaded {len(df)} jobs for trends analysis")
    
    # Get filters
    location = request.args.get('location')
    job = request.args.get('job')
    job_category = request.args.get('job_category')
    
    # Apply job category filter
    if job_category and job_category not in ["All", None, ""]:
        df = df[df['job_category'] == job_category]
        print(f"After job_category filter: {len(df)} jobs")
    
    # Apply location filter
    if location and location not in ["All locations", None, ""]:
        if location == "Remote":
            df = df[
                (df['location'].str.contains("Remote", case=False, na=False)) | 
                (df['is_remote'] == True) |
                (df['is_remote'] == "True")
            ]
        elif location == "California":
            df = df[df['state'] == 'California']
        elif location == "New York":
            df = df[df['state'] == 'New York']
        elif location == "Texas":
            df = df[df['state'] == 'Texas']
        print(f"After location filter: {len(df)} jobs")
    
    # Apply job title filter
    if job and job not in ["All jobs", None, ""]:
        df = df[df['title'].str.contains(job, case=False, na=False)]
        print(f"After job title filter: {len(df)} jobs")
    
    # Convert date_posted to datetime
    df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
    df = df.dropna(subset=['date_posted'])
    
    if df.empty:
        print("No date data after filtering")
        return jsonify({'date': [], 'postings': []})
    
    # Group by date and count postings
    daily_counts = df.groupby('date_posted').size().reset_index(name='postings')
    daily_counts = daily_counts.sort_values('date_posted')
    
    print(f"Returning {len(daily_counts)} date points")
    return jsonify({
        'date': daily_counts['date_posted'].dt.strftime('%Y-%m-%d').tolist(),
        'postings': daily_counts['postings'].tolist()
    })


if __name__ == "__main__":
    app.run(debug=True)
