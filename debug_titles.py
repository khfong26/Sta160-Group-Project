import pandas as pd
import os

try:
    df = pd.read_csv('data/processed/all_states_clean.csv')
    titles = df['title'].dropna().unique().tolist()
    
    with open('titles.txt', 'w', encoding='utf-8') as f:
        for t in sorted(titles):
            f.write(f"{t}\n")
            
    print(f"Wrote {len(titles)} titles to titles.txt")
except Exception as e:
    print(f"Error: {e}")
