import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def load_salary_data():
    path = os.path.join(DATA_DIR, "salaries_cleaned.csv")
    return pd.read_csv(path)

def load_skills_data():
    path = os.path.join(DATA_DIR, "skills_cleaned.csv")
    return pd.read_csv(path)
