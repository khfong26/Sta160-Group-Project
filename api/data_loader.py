import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def load_all_states_data():
    """Load the cleaned data for all states."""
    path = os.path.join(DATA_DIR, "all_states_clean.csv")
    return pd.read_csv(path)


def load_california_data():
    """Load the cleaned data for California."""
    path = os.path.join(DATA_DIR, "california_clean.csv")
    return pd.read_csv(path)


def load_newyork_data():
    """Load the cleaned data for New York."""
    path = os.path.join(DATA_DIR, "newyork_clean.csv")
    return pd.read_csv(path)


def load_texas_data():
    """Load the cleaned data for Texas."""
    path = os.path.join(DATA_DIR, "texas_clean.csv")
    return pd.read_csv(path)


def load_summary_data():
    """Load the summary data."""
    path = os.path.join(DATA_DIR, "summary_clean.csv")
    return pd.read_csv(path)


def load_skills_data():
    """Load the skills-cleaned CSV (contains parsed_skills column)."""
    path = os.path.join(
        DATA_DIR, "all_states_clean.csv")   # or skills_clean.csv if you have it
    df = pd.read_csv(path)

    # Ensure parsed_skills column exists
    if "parsed_skills" not in df.columns:
        raise KeyError(
            "parsed_skills column is missing from all_states_clean.csv")

    return df

