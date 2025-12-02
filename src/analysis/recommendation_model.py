import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2

# 1. Load job dataset (absolute path so Flask can find file)
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

    # Drop duplicates (VERY important)
    combined = combined.drop_duplicates(
        subset=["title", "company", "description"], keep="first"
    )

    return combined

# 2. Extract text from uploaded resume. Supports BOTH .txt and .pdf
def extract_resume_text(resume_file):
    filename = resume_file.filename.lower()

    #if its a PDF file
    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(resume_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    # Otherwise assume text file
    else:
        return resume_file.read().decode("utf-8", errors="ignore")

# 3. Build TF-IDF recommender - actual recommendation stuff here
def recommend_jobs(resume_text, top_k=5):
    jobs = load_job_data()

    # Use job descriptions for comparison
    job_texts = jobs["description"].fillna("")

    vectorizer = TfidfVectorizer(stop_words="english")
    job_matrix = vectorizer.fit_transform(job_texts)

    resume_vec = vectorizer.transform([resume_text])
    scores = cosine_similarity(resume_vec, job_matrix).flatten()

    jobs["score"] = scores
    return jobs.sort_values("score", ascending=False).head(top_k)
