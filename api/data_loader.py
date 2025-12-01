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

# Add to the end of api/data_loader.py

def load_all_jobs_combined():
    """Load and combine Data Analyst and Business Analyst jobs only."""
    import pandas as pd
    import os
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    all_dataframes = []
    
    # Data Analyst (YOUR data)
    try:
        da_jobs = pd.read_csv(os.path.join(DATA_DIR, "all_states_data_analyst_clean.csv"))
        da_jobs['job_category'] = 'Data Analyst'
        all_dataframes.append(da_jobs)
        print(f"Loaded {len(da_jobs)} Data Analyst jobs")
    except Exception as e:
        print(f"Could not load Data Analyst jobs: {e}")
    
    # Business Analyst (YOUR data)
    try:
        ba_jobs = pd.read_csv(os.path.join(DATA_DIR, "all_states_business_analyst_clean.csv"))
        ba_jobs['job_category'] = 'Business Analyst'
        all_dataframes.append(ba_jobs)
        print(f"Loaded {len(ba_jobs)} Business Analyst jobs")
    except Exception as e:
        print(f"Could not load Business Analyst jobs: {e}")
    
    # Combine all available dataframes
    if all_dataframes:
        all_jobs = pd.concat(all_dataframes, ignore_index=True)
        print(f"Total combined jobs: {len(all_jobs)}")
        return all_jobs
    else:
        print("No job data loaded!")
        return pd.DataFrame()