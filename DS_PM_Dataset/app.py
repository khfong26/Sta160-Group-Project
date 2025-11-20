# app.py  —— Robust Job Market Dashboard (auto column mapping)
# run: streamlit run app.py

from pathlib import Path
import re
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Job Market Dashboard", layout="wide")

# ---------- helpers ----------
def annualize_from_range(min_amt, max_amt, period):
    # period in {"hour","day","week","month","year"} (best effort)
    if pd.isna(min_amt) and pd.isna(max_amt):
        return np.nan
    vals = [v for v in [min_amt, max_amt] if pd.notna(v)]
    if not vals:
        return np.nan
    v = float(np.mean(vals))
    p = (str(period) if isinstance(period, str) else "").lower()
    if "hour" in p or p == "hr":   v *= 40 * 52
    elif "day" in p:               v *= 5 * 52
    elif "week" in p:              v *= 52
    elif "month" in p:             v *= 12
    # if "year" leave as is
    return v if 10000 < v < 1_000_000 else np.nan

def parse_loose_salary(text):
    if not isinstance(text, str): return np.nan
    t = text.lower().replace(",", "")
    nums = [float(x) for x in re.findall(r"\d+\.?\d*", t)]
    if not nums: return np.nan
    v = float(np.mean(nums))
    # detect hourly keywords
    if any(k in t for k in ["/hr","hour","hr"] ) and v < 500: v *= 40*52
    return v if 10000 < v < 1_000_000 else np.nan

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower().strip(): c for c in df.columns}
    # job title
    for cand in ["job_title","title","position","role"]:
        if cand in cols: df.rename(columns={cols[cand]:"job_title"}, inplace=True); break
    if "job_title" not in df: df["job_title"] = np.nan

    # company
    for cand in ["company","company_name","employer","employer_name","hiring_company"]:
        if cand in cols: df.rename(columns={cols[cand]:"company"}, inplace=True); break
    if "company" not in df: df["company"] = np.nan

    # location (try city + state)
    loc = None
    if "location" in cols: loc = cols["location"]
    elif "city" in cols and "state" in cols:
        df["location"] = df[cols["city"]].astype(str) + ", " + df[cols["state"]].astype(str)
    elif "state" in cols:
        df["location"] = df[cols["state"]]
    else:
        df["location"] = np.nan

    # salary text
    for cand in ["salary","compensation","pay","pay_text"]:
        if cand in cols: df.rename(columns={cols[cand]:"salary"}, inplace=True); break

    # try numeric range from jobspy style columns
    min_col = next((cols[c] for c in ["min_amount","min_salary","salary_min"] if c in cols), None)
    max_col = next((cols[c] for c in ["max_amount","max_salary","salary_max"] if c in cols), None)
    per_col = next((cols[c] for c in ["pay_period","compensation_period","period"] if c in cols), None)

    if min_col or max_col:
        df["salary_clean"] = annualize_from_range(
            pd.to_numeric(df[min_col], errors="coerce") if min_col else np.nan,
            pd.to_numeric(df[max_col], errors="coerce") if max_col else np.nan,
            df[per_col] if per_col else "year"
        )
    else:
        if "salary" in df.columns:
            df["salary_clean"] = df["salary"].apply(parse_loose_salary)
        else:
            df["salary_clean"] = np.nan

    # tidy
    for c in ["job_title","company","location"]:
        df[c] = df[c].astype(str).str.strip()
    return df

@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return standardize_columns(df)

# ---------- data sources ----------
ROOT = Path(__file__).parent
DATA = ROOT / "data"
sources = {
    "All States": DATA / "all_states_jobs.csv",
    "California": DATA / "california_jobs.csv",
    "New York":  DATA / "newyork_jobs.csv",
    "Texas":     DATA / "texas_jobs.csv",
}

# ---------- sidebar ----------
st.sidebar.header("Options")
choice = st.sidebar.selectbox("Select dataset", list(sources.keys()))
df = load_csv(sources[choice])

# dynamic filters
titles = sorted([t for t in df["job_title"].dropna().unique() if str(t).strip()])
picked = st.sidebar.multiselect("Job titles", titles, titles[:5] if titles else [])
if picked: df = df[df["job_title"].isin(picked)]

min_sal = int(np.nanpercentile(df["salary_clean"], 5)) if df["salary_clean"].notna().any() else 20000
max_sal = int(np.nanpercentile(df["salary_clean"],95)) if df["salary_clean"].notna().any() else 250000
lo, hi = st.sidebar.slider("Salary range (annual USD)", min_sal, max_sal, (min_sal, max_sal))
df = df[(df["salary_clean"].fillna(min_sal) >= lo) & (df["salary_clean"].fillna(min_sal) <= hi)]

# ---------- header & KPIs ----------
st.title(f"📊 Job Market Dashboard — {choice}")
c1, c2, c3 = st.columns(3)
c1.metric("Job Count", f"{len(df):,}")
c2.metric("Unique Companies", df["company"].nunique())
median = df["salary_clean"].median()
c3.metric("Median Salary", f"${median:,.0f}" if pd.notna(median) else "—")

st.divider()

# ---------- charts ----------
if not df.empty:
    if df["salary_clean"].notna().any():
        fig = px.histogram(df, x="salary_clean", nbins=30,
                           title="Salary Distribution (Annual USD)",
                           labels={"salary_clean":"Salary (USD)"})
        st.plotly_chart(fig, use_container_width=True)

    if df["job_title"].notna().any():
        top = df["job_title"].value_counts().reset_index().rename(columns={"index":"Job Title","job_title":"Count"})
        st.plotly_chart(px.bar(top.head(20), x="Job Title", y="Count", title="Top Job Titles"),
                        use_container_width=True)

    if df["location"].notna().any():
        loc = df["location"].value_counts().reset_index().rename(columns={"index":"Location","location":"Count"})
        st.plotly_chart(px.bar(loc.head(20), x="Location", y="Count", title="Top Locations"),
                        use_container_width=True)

# ---------- table + download ----------
st.subheader("Raw Data")
st.dataframe(df.head(300), use_container_width=True)
st.download_button("Download filtered CSV", df.to_csv(index=False).encode("utf-8"),
                   "filtered_jobs.csv", "text/csv")