import streamlit as st
import json
import os
from rapidfuzz import process
import pandas as pd

# === File Paths ===
DATA_FOLDER = "/Users/mathildekrafft/Desktop/class SA 2025/Text mining/Insights from Text Data 2025 Day 1/Rmd files"
FUNCTIONS_FILE = os.path.join(DATA_FOLDER, "functions_clean_expanded.json")
CODEBLOCKS_FILE = os.path.join(DATA_FOLDER, "codeblocks_clean(1).json")

# === Load JSON Files ===
with open(FUNCTIONS_FILE, "r", encoding="utf-8") as f:
    functions_data = json.load(f)

with open(CODEBLOCKS_FILE, "r", encoding="utf-8") as f:
    codeblocks_data = json.load(f)

# === Build Function Lookup ===
functions_lookup = {item["function"]: item for item in functions_data}

# === Link Code Examples to Functions ===
for block in codeblocks_data:
    code = block.get("code", "")
    for func_name in functions_lookup:
        if func_name in code:
            functions_lookup[func_name].setdefault("examples", []).append(code)

# === Prepare DataFrame for Display ===
merged_data = []
for func in functions_lookup.values():
    merged_data.append({
        "function_name": func.get("function", ""),
        "package": func.get("package", ""),
        "explanation": func.get("explanation", ""),
        "examples": func.get("examples", [])
    })

df = pd.DataFrame(merged_data)

# === Streamlit App ===
st.set_page_config(page_title="R Function Search", layout="wide")
st.title("🔍 R Function Search with Fuzzy Matching")

# === Sidebar Filters ===
packages = sorted(df["package"].dropna().unique())
selected_package = st.sidebar.selectbox("📦 Filter by Package", ["All"] + packages)

# === Search Input ===
query = st.text_input("🔎 Enter function name (fuzzy search):")

# === Apply Package Filter ===
filtered_df = df if selected_package == "All" else df[df["package"] == selected_package]

# === Perform Fuzzy Search ===
results = []
if query:
    choices = filtered_df["function_name"].tolist()
    matches = process.extract(query, choices, limit=10, score_cutoff=60)
    for match, score, idx in matches:
        row = filtered_df.iloc[idx]
        results.append(row)

# === Display Results ===
if results:
    st.write(f"### Top Matches for '{query}':")
    for row in results:
        st.markdown(f"""
        **Function:** `{row['function_name']}`  
        **Package:** `{row['package']}`  
        **Explanation:** {row['explanation']}  
        **Code Examples:**  
        """)
        for code in row['examples']:
            st.code(code, language='r')
        st.markdown("---")
else:
    if query:
        st.warning("No matches found. Try another keyword.")

# === Download Button ===
if results:
    export_df = pd.DataFrame(results)
    csv_data = export_df.to_csv(index=False)
    st.download_button("📥 Download Results as CSV", data=csv_data, file_name="search_results.csv", mime="text/csv")