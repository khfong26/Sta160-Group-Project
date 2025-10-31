import pandas as pd
import os
# hello
#t
# === 1. Set working directory ===
path = "/Users/royho/Desktop/World Bank Data - Datasets V2"
os.chdir(path)

# === 2. Dataset filenames ===
files = {
    "cpi": "Consumer price index (2010 = 100).csv",
    "food": "Conusmer Prices, Food Indices (2015 = 100).csv",
    "exchange": "Exchange Rates.csv",
    "gdp": "GDP (Current US$).csv",
    "inflation": "Inflation - Avg consumer prices index.csv",
    "population": "Population, total.csv"
}

dfs = {}

# === 3. Load and clean ===
for key, filename in files.items():
    print(f"\n🔹 Loading {filename}...")
    df = pd.read_csv(filename, low_memory=False)
    df.columns = df.columns.str.strip()

    # Handle V2 column pattern:
    # ['A', 'Annual', 'ALB', 'Albania', 'WB_WDI_FP_CPI_TOTL', 'Consumer price index (2010 = 100)', '1960', '1961', ...]
    if len(df.columns) < 8:
        print(f"⚠️ {filename} does not match expected structure. Skipping.")
        continue

    # Rename and keep relevant columns
    df.rename(
        columns={
            df.columns[2]: "Country Code",
            df.columns[3]: "Country Name"
        },
        inplace=True
    )

    # Extract year columns dynamically (start from column index 6 onward)
    year_cols = [col for col in df.columns if col.isdigit()]
    df = df[["Country Name", "Country Code"] + year_cols]

    # Melt into long format
    df = df.melt(id_vars=["Country Name", "Country Code"],
                 var_name="Year", value_name=key)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    dfs[key] = df

print("\n✅ Loaded datasets:", list(dfs.keys()))

# === 4. Merge ===
merged = dfs["cpi"]
for key in ["food", "gdp", "inflation", "exchange", "population"]:
    if key in dfs:
        merged = pd.merge(merged, dfs[key], on=[
                          "Country Name", "Country Code", "Year"], how="outer")

# === 5. Filter for North American countries ===
countries = ["United States", "Canada", "Mexico"]
merged = merged[merged["Country Name"].isin(countries)]

# === 6. Sort, fill, save ===
merged.sort_values(by=["Country Name", "Year"], inplace=True)
merged = merged.groupby("Country Name").ffill().bfill()

output_path = os.path.join(path, "Cleaned_WorldBank_FoodInflation.csv")
merged.to_csv(output_path, index=False)

print("\n✅ Cleaning complete!")
print(f"Saved to: {output_path}")
print("\nPreview:")
print(merged.head())
