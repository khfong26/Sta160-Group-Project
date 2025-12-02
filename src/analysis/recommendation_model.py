import os
import json
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2

# Load all the skills from the skill.json file
SKILLS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "cleaning", "skills.json")

with open(SKILLS_JSON_PATH, "r") as f:
    SKILL_TERMS = json.load(f)


# Load all job data from processed CSVs
def load_job_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    folder_path = os.path.join(base_dir, "data", "processed")

    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".csv")
    ]

    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not dfs:
        raise ValueError("No CSV files found in processed folder.")

    combined = pd.concat(dfs, ignore_index=True)

    # Remove duplicates
    combined = combined.drop_duplicates(
        subset=["title", "company", "description"], keep="first"
    )

    return combined


# Extract resume text (PDF or TXT)
def extract_resume_text(resume_file):
    filename = resume_file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(resume_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    return resume_file.read().decode("utf-8", errors="ignore")


# Extract experience from resume
def extract_years_of_experience(resume_text):
    resume_lower = resume_text.lower()

    # If resume mentions "intern" assume 0 years
    if "intern" in resume_lower:
        return 0

    # Look for patterns like "2 years", "3+ years"
    match = re.search(r"(\d+)\+?\s*years?", resume_lower)
    if match:
        return int(match.group(1))

    # Default assumption
    return 1


# Extract skill matches from resume
def extract_resume_skills(resume_text):
    resume_lower = resume_text.lower()
    found = {s for s in SKILL_TERMS if s.lower() in resume_lower}
    return found


# Extract required years of experience from job DESCRIPTION
def extract_years_from_description(text):
    if pd.isna(text):
        return 0

    text = str(text).lower()

    # Match simple patterns like "2 years", "3+ years"
    match = re.search(r"(\d+)\+?\s*years?", text)
    if match:
        return int(match.group(1))

    # Match ranges like "0-2 years", "1-3 years"
    range_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", text)
    if range_match:
        return int(range_match.group(1))

    return 0


# Main recommendation function
def recommend_jobs(resume_text, top_k=5):
    # 1. Load job data
    jobs = load_job_data()

    # 2. Determine candidate experience level from resume
    user_years = extract_years_of_experience(resume_text)

    # 3. Filter out senior roles by TITLE (we are new grads)
    senior_terms = ["senior", "sr.", "lead", "principal", "director", "manager"]
    pattern = "|".join(senior_terms)
    jobs = jobs[~jobs["title"].str.lower().str.contains(pattern, na=False)]

    # 4. Extract required years of experience from job DESCRIPTION
    jobs["min_exp"] = jobs["description"].apply(extract_years_from_description)

    # keep jobs that are not too far above the student's level
    jobs = jobs[jobs["min_exp"] <= user_years + 1].copy()

    # 5. Build TF–IDF matrix using title + skills + description
    job_texts = (
        jobs["title"].fillna("") + " " +
        jobs["skills"].fillna("") + " " +
        jobs["description"].fillna("")
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_df=0.85,
        min_df=3,
        sublinear_tf=True,
        ngram_range=(1, 2),
    )

    job_matrix = vectorizer.fit_transform(job_texts)
    
    resume_skills = extract_resume_skills(resume_text)
    resume_for_tfidf = resume_text + " " + " ".join(resume_skills)

    resume_vec = vectorizer.transform([resume_for_tfidf])
    tfidf_scores = cosine_similarity(resume_vec, job_matrix).flatten()

    # 5a. normalize tfidf to [0, 1]
    tfidf_min, tfidf_max = tfidf_scores.min(), tfidf_scores.max()
    if tfidf_max > tfidf_min:
        tfidf_norm = (tfidf_scores - tfidf_min) / (tfidf_max - tfidf_min)
    else:
        tfidf_norm = tfidf_scores  # all equal

    jobs["tfidf_score"] = tfidf_norm

    # 6. Skill overlap score (normalized) + record matched skills
    def skill_overlap(job_skill_field):
        if pd.isna(job_skill_field):
            return set(), 0.0
        job_skillset = {
            s.strip().lower() for s in str(job_skill_field).split(",") if s.strip()
        }
        overlap = resume_skills.intersection(job_skillset)
        if not job_skillset:
            score = 0.0
        else:
            score = len(overlap) / len(job_skillset)  # 0–1
        return overlap, score

    overlap_results = jobs["skills"].apply(skill_overlap)
    jobs["matched_skills"] = overlap_results.apply(lambda x: sorted(x[0]))
    jobs["skill_score"] = overlap_results.apply(lambda x: x[1])

    # 7. Experience bonus: closer to user_years is slightly better (also 0–1)
    def experience_bonus(min_exp):
        # already filtered min_exp <= user_years + 1
        gap = abs(min_exp - user_years)
        return 1.0 / (1.0 + gap)

    jobs["exp_bonus"] = jobs["min_exp"].apply(experience_bonus)

    # 8. Final combined score for ranking
    #    TF-IDF and skill_score are both in [0,1], exp_bonus in (0,1]
    jobs["final_score"] = (
        0.55 * jobs["tfidf_score"] +
        0.35 * jobs["skill_score"] +
        0.10 * jobs["exp_bonus"]
    )

    # Return the top matching jobs
    return jobs.sort_values("final_score", ascending=False).head(top_k)
