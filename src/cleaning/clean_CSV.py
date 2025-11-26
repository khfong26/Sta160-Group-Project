import pandas as pd
import json
import os
import re
import ast

RAW = "data"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

def load(name):
    return pd.read_csv(os.path.join(RAW, name))

#clean the HTML and remove all of the tags, broken tags, etc. 
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

    # 3. Replace weird hyphen artifacts
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")

    # 4. Remove excess whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text

# cleans skills 
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

# main cleaning function 
def clean_jobs(input_name, output_name):
    print(f"Cleaning {input_name} → {output_name}")

    df = load(input_name)

    # Normalize column names  
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Fix bad column name 
    if "statethis" in df.columns:
        df = df.rename(columns={"statethis": "state"})

    #  Clean HTML columns 
    html_cols = ["description", "company_description"]
    for col in html_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_html)

    #  Clean skills
    if "skills" in df.columns:
        df["skills"] = df["skills"].apply(clean_skills)

    #  Convert numeric salary values 
    for col in ["min_amount", "max_amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    #  Drop noisy/useless columns we can go back and see if we want any of these but i doubt it 
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

    #  Final whitespace cleanup for all text columns 
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    #  Save cleaned file 
    df.to_csv(os.path.join(PROCESSED, output_name), index=False)
    print(f"✓ Saved cleaned: {output_name}\n")

# run this for all all CSV files that jobspy outputs 
clean_jobs("../data/raw/california_software.csv", "ca_sw_clean.csv")
clean_jobs("../data/raw/newyork_software.csv", "ny_sw_clean.csv")
clean_jobs("../data/raw/texas_software.csv", "tx_sw_clean.csv")
clean_jobs("../data/raw/all_states_software.csv", "all_sw_clean.csv")
clean_jobs("../data/raw/summary_report_software.csv", "summary_sw_clean.csv")

clean_jobs("../data/raw/california_db.csv", "ca_db_clean.csv")
clean_jobs("../data/raw/newyork_db.csv", "ny_db_clean.csv")
clean_jobs("../data/raw/texas_db.csv", "tx_db_clean.csv")
clean_jobs("../data/raw/all_states_db.csv", "all_db_clean.csv")
clean_jobs("../data/raw/summary_report_db.csv", "summary_db_clean.csv")