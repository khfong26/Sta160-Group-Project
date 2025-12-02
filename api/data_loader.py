import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# Global cache
_ALL_STATES_DATA = None

def load_all_states_data():
    """Load the cleaned data for all states from multiple files. Cached."""
    global _ALL_STATES_DATA
    if _ALL_STATES_DATA is not None:
        return _ALL_STATES_DATA

    files = [
        "all_states_clean.csv",
        "all_states_business_analyst_clean.csv",
        "all_states_data_analyst_clean.csv",
        "all_states_machine_learning_engineer_clean.csv",
        "all_states_software_engineer_clean.csv",
        "all_states_DS_PM_clean.csv"
    ]
    
    dfs = []
    for f in files:
        path = os.path.join(DATA_DIR, f)
        if os.path.exists(path):
            try:
                dfs.append(pd.read_csv(path))
            except Exception as e:
                print(f"Error loading {f}: {e}")
    
    if not dfs:
        _ALL_STATES_DATA = pd.DataFrame()
    else:
        _ALL_STATES_DATA = pd.concat(dfs, ignore_index=True)
        
    return _ALL_STATES_DATA


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

