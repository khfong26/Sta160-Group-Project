import pandas as pd
import json
import os
import re
import ast
SKILLS_JSON_PATH = os.path.join(os.path.dirname(__file__), "skills.json")

with open(SKILLS_JSON_PATH, "r") as f:
    SKILL_TERMS = json.load(f)

RAW = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

def load(name):
    return pd.read_csv(os.path.join(RAW, name))


# Clean the HTML and remove all of the tags, broken tags, etc.
def clean_html(text):
    if pd.isna(text):
        return ""
    text = str(text)

    # Remove all <tags>
    text = re.sub(r"<[^>]+>", " ", text)

    # convert common HTML entities
    html_entities = {
        "&nbsp;": " ",
        "&rsquo;": "'",
        "&lsquo;": "'",
        "&rdquo;": '"',
        "&ldquo;": '"',
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"'
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Replace weird hyphen artifacts
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")

    # Remove excess whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# cleans skills if JobSpy returns list-like strings
def clean_skills(text):
    """ Convert list-like strings ['A','B'] → A, B """
    if pd.isna(text):
        return ""
    text = str(text)
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return ", ".join([str(i) for i in parsed])
        return text
    except:
        return text



# new stuff here: spaCy Skill Extraction 

import spacy
from spacy.matcher import PhraseMatcher

# Load spaCy model 
nlp = spacy.load("en_core_web_lg")


# Build PhraseMatcher from JSON skill list
matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(skill) for skill in SKILL_TERMS]
matcher.add("SKILLS", patterns)

def extract_skills_nlp(text):
    """Extract skills using spaCy PhraseMatcher"""
    if pd.isna(text):
        return ""

    doc = nlp(text.lower())
    matches = matcher(doc)
    skills = [doc[start:end].text for match_id, start, end in matches]

    return ", ".join(sorted(set(skills)))


#main cleaning function
def clean_jobs(input_name, output_name):
    print(f"Cleaning {input_name} → {output_name}")

    df = load(input_name)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Fix bad column name
    if "statethis" in df.columns:
        df = df.rename(columns={"statethis": "state"})

    # Clean HTML columns
    html_cols = ["description", "company_description"]
    for col in html_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_html)

    # NEW: Extract skills from description using spaCy
    if "description" in df.columns:
        df["parsed_skills"] = df["description"].apply(extract_skills_nlp)

    # Clean "skills" column if it exists
    if "skills" in df.columns:
        df["skills"] = df["skills"].apply(clean_skills)

    # Convert numeric salary values
    for col in ["min_amount", "max_amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop noisy/useless columns
    cols_to_drop = [
        "emails",
        "job_url_direct",
        "company_logo",
        "company_url_direct",
        "company_addresses",
        "vacancy_count",
        "work_from_home_type"
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")

    # Final whitespace cleanup for all text columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Save cleaned file
    df.to_csv(os.path.join(PROCESSED, output_name), index=False)
    print(f"✓ Saved cleaned: {output_name}\n")



#run all of it and save it 

clean_jobs("california_jobs.csv", "california_clean.csv")
clean_jobs("newyork_jobs.csv", "newyork_clean.csv")
clean_jobs("texas_jobs.csv", "texas_clean.csv")
clean_jobs("all_states_jobs.csv", "all_states_clean.csv")
clean_jobs("summary_report.csv", "summary_clean.csv")

# Clean Data Analyst files
clean_jobs("california_data_analyst_jobs.csv", "california_data_analyst_clean.csv")
clean_jobs("newyork_data_analyst_jobs.csv", "newyork_data_analyst_clean.csv")
clean_jobs("texas_data_analyst_jobs.csv", "texas_data_analyst_clean.csv")
clean_jobs("all_states_data_analyst_jobs.csv", "all_states_data_analyst_clean.csv")
clean_jobs("data_analyst_summary_report.csv", "data_analyst_summary_clean.csv")

# Clean Business Analyst files
clean_jobs("california_business_analyst_jobs.csv", "california_business_analyst_clean.csv")
clean_jobs("newyork_business_analyst_jobs.csv", "newyork_business_analyst_clean.csv")
clean_jobs("texas_business_analyst_jobs.csv", "texas_business_analyst_clean.csv")
clean_jobs("all_states_business_analyst_jobs.csv", "all_states_business_analyst_clean.csv")
clean_jobs("business_analyst_summary_report.csv", "business_analyst_summary_clean.csv")

# Clean Software Engineer files
clean_jobs("california_software_engineer_jobs.csv", "california_software_engineer_clean.csv")
clean_jobs("newyork_software_engineer_jobs.csv", "newyork_software_engineer_clean.csv")
clean_jobs("texas_software_engineer_jobs.csv", "texas_software_engineer_clean.csv")
clean_jobs("all_states_software_engineer_jobs.csv", "all_states_software_engineer_clean.csv")
clean_jobs("software_engineer_summary_report.csv", "software_engineer_summary_clean.csv")

# Clean Machine Learning Engineer files
clean_jobs("california_machine_learning_engineer_jobs.csv", "california_machine_learning_engineer_clean.csv")
clean_jobs("newyork_machine_learning_engineer_jobs.csv", "newyork_machine_learning_engineer_clean.csv")
clean_jobs("texas_machine_learning_engineer_jobs.csv", "texas_machine_learning_engineer_clean.csv")
clean_jobs("all_states_machine_learning_engineer_jobs.csv", "all_states_machine_learning_engineer_clean.csv")
clean_jobs("machine_learning_engineer_summary_report.csv", "machine_learning_engineer_summary_clean.csv")
