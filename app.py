import streamlit as st
import json
import pandas as pd
import requests
import numpy as np
from rapidfuzz import process
import re

# === Configuration ===
st.set_page_config(page_title="Text Mining R Helper", layout="wide", page_icon="🧚🏼‍♂️")

# === Load Data from GitHub ===
@st.cache_data
def load_data():
    FUNCTIONS_URL = "https://raw.githubusercontent.com/Mathildekrafft2001/text-mining-app/main/functions_enriched_final.json"
    CODEBLOCKS_URL = "https://raw.githubusercontent.com/Mathildekrafft2001/text-mining-app/main/codeblocks_clean.json"
    
    functions_data = requests.get(FUNCTIONS_URL).json()
    codeblocks_data = requests.get(CODEBLOCKS_URL).json()
    
    # Build function lookup
    functions_lookup = {item["function"]: item for item in functions_data}
    
    # Link code examples to functions
    for block in codeblocks_data:
        code = block.get("code", "")
        for func_name in functions_lookup:
            pattern = rf"\b{re.escape(func_name)}\s*\("
            if re.search(pattern, code):
                functions_lookup[func_name].setdefault("examples", []).append(code)
    
    return functions_lookup, functions_data

functions_lookup, functions_data = load_data()

# === Sidebar Navigation ===
st.sidebar.title("Menu")
page = st.sidebar.radio("Choose a tool:", 
                        ["Function Search", "Package Explorer", "Text Mining Calculator"])

#==============================
# PAGE 0.5 : HELP PAGE
#==============================
if st.session_state.get("page") == "Help":
    st.title(" You got this, you beautiful queen! ")

    # Confetti animation
    st.balloons()

    # Dancing panda GIF from Giphy
    st.image("https://media.giphy.com/media/lJNoBCvQYp7nq/giphy.gif", width=400)

    st.markdown("### Everything is under control! Never give up nanana 🎵 !")

    # Back button
    if st.button("Back to Function Search"):
        st.session_state["page"] = "Function Search"
        st.rerun()

# ============================================
# PAGE 1: FUNCTION SEARCH WITH AUTOCOMPLETE
# ============================================
elif page == "Function Search":
    st.title("R Function Search Engine")
    st.markdown("*Search for R functions with autocomplete, detailed explanations, and code examples*")
    
    # === Filters ===
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get all function names for autocomplete
        all_functions = sorted([f["function"] for f in functions_data])
        
        # Search input with autocomplete
        query = st.selectbox(
            "Search for a function (start typing):",
            options=[""] + all_functions,
            format_func=lambda x: "Type to search..." if x == "" else x
        )
    
    with col2:

        if st.button("Press if you need help"):
                st.session_state["page"] = "Help"
                st.rerun()


    # === Display Results ===
    if query and query != "":
        func_data = functions_lookup.get(query)
        
        if func_data:
            # Function header
            st.markdown(f"## `{func_data['function']}`")
            st.markdown(f"**Package:** `{func_data.get('package', 'unknown')}`")
            
            # Explanation
            st.markdown("### Explanation")
            st.info(func_data.get('explanation', 'No explanation available.'))
            
            # Arguments
            arguments = func_data.get('arguments', [])
            if arguments:
                st.markdown("### Arguments")
                args_df = pd.DataFrame(arguments)
                st.table(args_df)
            else:
                st.markdown("### Arguments")
                st.caption("No arguments documented.")
            
            # Code examples
            examples = func_data.get('examples', [])
            if examples:
                st.markdown("### Code Examples")
                for i, code in enumerate(examples[:5], 1):
                    with st.expander(f"Example {i}"):
                        st.code(code, language='r')
            else:
                st.markdown("### Code Examples")
                st.caption("No code examples available for this function.")
        else:
            st.warning("Function not found in database.")
    
    elif query == "":
        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown("""
        - Start typing in the search box to see autocomplete suggestions
        - Filter by package to narrow down results
        - Click on a function to see detailed documentation and examples
        """)
        
        # Show some popular functions
        st.markdown("### Popular Functions")
        popular = ["unnest_tokens", "filter", "mutate", "ggplot", "count", "group_by", 
                   "left_join", "str_detect", "pivot_longer", "summarize"]
        
        cols = st.columns(5)
        for i, func in enumerate(popular):
            with cols[i % 5]:
                if st.button(f"`{func}`", key=f"pop_{func}"):
                    st.rerun()

# ============================================
# PAGE 2: PACKAGE EXPLORER
# ============================================
elif page == "Package Explorer":
    st.title("R Package Explorer")
    st.markdown("*Explore R packages and their functions for text mining*")
    
    # Get package statistics
    package_stats = {}
    for func in functions_data:
        pkg = func.get('package', 'unknown')
        if pkg not in package_stats:
            package_stats[pkg] = []
        package_stats[pkg].append(func['function'])
    
    # Sort packages by number of functions
    sorted_packages = sorted(package_stats.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Package selector
    selected_pkg = st.selectbox(
        "Select a package to explore:",
        options=[pkg for pkg, _ in sorted_packages],
        format_func=lambda x: f"{x} ({len(package_stats[x])} functions)"
    )
    
    if selected_pkg:
        st.markdown(f"## Package: `{selected_pkg}`")
        st.markdown(f"**Number of functions:** {len(package_stats[selected_pkg])}")
        
        # Package descriptions
        package_descriptions = {
            "tidytext": "Tidy tools for text mining - convert text to/from tidy formats",
            "dplyr": "Data manipulation - filter, select, mutate, summarize data frames",
            "stringr": "String manipulation - detect, replace, extract patterns in text",
            "ggplot2": "Data visualization - create elegant graphics using grammar of graphics",
            "textrecipes": "Text preprocessing for modeling - tokenization, TF-IDF, embeddings",
            "tidyr": "Data tidying - reshape data between wide and long formats",
            "recipes": "Preprocessing interface for modeling - define reusable preprocessing steps",
            "parsnip": "Unified modeling interface - consistent API for different model types",
            "workflows": "Bundle preprocessing and models - keep analysis reproducible",
            "tune": "Hyperparameter tuning - fit and evaluate models across resamples",
            "rsample": "Data resampling - create training/test splits and cross-validation folds",
            "quanteda": "Quantitative text analysis - corpus management, DFM creation",
            "tm": "Text mining framework - traditional text mining workflows",
            "stopwords": "Stopword lists - multilingual stopwords from various sources",
            "base": "Base R functions - fundamental R operations",
            "stats": "Statistical functions - modeling and statistical tests"
        }
        
        if selected_pkg in package_descriptions:
            st.info(f"**Description:** {package_descriptions[selected_pkg]}")
        
        # Show functions in package
        st.markdown("### Functions in this package:")
        
        # Create expandable sections for each function
        for func_name in sorted(package_stats[selected_pkg]):
            func_data = functions_lookup.get(func_name, {})
            with st.expander(f"**`{func_name}()`**"):
                st.markdown(func_data.get('explanation', 'No explanation available.'))
                
                # Show arguments if available
                args = func_data.get('arguments', [])
                if args:
                    st.markdown("**Arguments:**")
                    for arg in args:
                        st.markdown(f"- `{arg.get('name')}`: {arg.get('description')}")

# ============================================
# PAGE 3: TEXT MINING CALCULATOR
# ============================================
elif page == "Text Mining Calculator":
    st.title("Text Mining Calculator")
    st.markdown("*Calculate TF-IDF and Type-Token Ratio for your text mining projects*")
    
    # Calculator type selector
    calc_type = st.radio("Select calculation:", ["TF-IDF Calculator", "Type-Token Ratio"])
    
    # === TF-IDF CALCULATOR ===
    if calc_type == "TF-IDF Calculator":
        st.markdown("## TF-IDF Calculator")
        st.markdown("""
        **TF-IDF** (Term Frequency - Inverse Document Frequency) measures how important a word is to a document in a collection.
        
        - **TF** (Term Frequency): How often a term appears in a document
        - **IDF** (Inverse Document Frequency): How rare the term is across all documents
        - **TF-IDF** = TF × IDF = (term count / total tokens) × ln(N / n)
        
        Where:
        - N = Total number of documents
        - n = Number of documents containing the term
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        
        with col1:
            term_count = st.number_input(
                "Term count in this document:",
                min_value=0,
                value=5,
                help="How many times does the term appear in this document?"
            )

            total_tokens = st.number_input(
                "Total tokens in this document:",
                min_value=1,
                value=100,
                help="Total number of words/tokens in the document"
            )

        
        with col2:
            total_docs = st.number_input(
                "Total number of documents (N):",
                min_value=1,
                value=100,
                help="Total number of documents in the corpus"
            )

            docs_with_term = st.number_input(
                "Documents containing term (n):",
                min_value=1,
                value=10,
                help="How many documents contain this term?"
            )
        
        if st.button("Calculate TF-IDF", type="primary"):
            if docs_with_term > total_docs:
                st.error("Documents containing term cannot exceed total documents!")
            else:
                # Calculate TF
                tf = term_count / total_tokens

                # Calculate IDF
                idf = np.log(total_docs / docs_with_term)
                
                # Calculate TF-IDF
                tf_idf = tf * idf
                
                # Display results
                st.markdown("### Results")
                res_col1, res_col2, res_col3 = st.columns(3)
                
                with res_col1:
                    st.metric("Term Frequency (TF)", f"{tf:.7f}")
                
                with res_col2:
                    st.metric("IDF", f"{idf:.7f}")
                
                with res_col3:
                    st.metric("TF-IDF", f"{tf_idf:.7f}")
                
                # Interpretation
                st.markdown("### Interpretation")
                if tf_idf > 5:
                    st.success(f"**High importance**: This term is very important to this document (appears frequently and is rare in the corpus).")
                elif tf_idf > 2:
                    st.info(f"**Moderate importance**: This term is moderately important to this document.")
                else:
                    st.warning(f"**Low importance**: This term is common across documents or appears rarely in this document.")
                
                # Formula breakdown
                with st.expander("See calculation steps"):
                    st.markdown(f"""
                    
                    **Step 1:** Calculate TF
                    ```
                    TF = term_count / total_tokens
                    TF = {term_count} / {total_tokens}
                    TF = {tf:.7f}
                    ```

                    **Step 2:** Calculate IDF
                    ```
                    IDF = ln(N / n)
                    IDF = ln({total_docs} / {docs_with_term})
                    IDF = {idf:.7f}
                    ```
                    
                    **Step 3:** Calculate TF-IDF
                    ```
                    TF-IDF = TF × IDF
                    TF-IDF = {tf} × {idf:.7f}
                    TF-IDF = {tf_idf:.7f}
                    ```
                    """)
    
    # === TYPE-TOKEN RATIO ===
    else:
        st.markdown("## Type-Token Ratio (TTR) Calculator")
        st.markdown("""
        **Type-Token Ratio** measures lexical diversity (vocabulary richness) in a text.
        
        - **Types**: Number of unique words (vocabulary)
        - **Tokens**: Total number of words
        - **TTR** = Types / Tokens
        
        **Interpretation:**
        - TTR close to 1.0 → High diversity (many unique words)
        - TTR close to 0.0 → Low diversity (repetitive text)
        """)
        
        st.markdown("---")
        
        # Input method selector
        input_method = st.radio("Input method:", ["Enter counts manually", "Paste text"])
        
        if input_method == "Enter counts manually":
            col1, col2 = st.columns(2)
            
            with col1:
                num_types = st.number_input(
                    "Number of unique words (Types):",
                    min_value=1,
                    value=50,
                    help="Count of distinct/unique words"
                )
            
            with col2:
                num_tokens = st.number_input(
                    "Total number of words (Tokens):",
                    min_value=1,
                    value=100,
                    help="Total word count including repetitions"
                )
            
            if st.button("Calculate TTR", type="primary"):
                if num_types > num_tokens:
                    st.error("Unique words cannot exceed total words!")
                else:
                    ttr = num_types / num_tokens
                    
                    # Display results
                    st.markdown("### Results")
                    
                    res_col1, res_col2, res_col3 = st.columns(3)
                    
                    with res_col1:
                        st.metric("Types (Unique)", f"{num_types}")
                    
                    with res_col2:
                        st.metric("Tokens (Total)", f"{num_tokens}")
                    
                    with res_col3:
                        st.metric("TTR", f"{ttr:.4f}")
                    
                    # Visual indicator
                    st.progress(ttr, text=f"Lexical Diversity: {ttr:.2%}")
                    
                    # Interpretation
                    st.markdown("### Interpretation")
                    if ttr >= 0.7:
                        st.success(f"**Very High Diversity** ({ttr:.2%}): Rich vocabulary, low repetition. Typical of literary texts, academic writing.")
                    elif ttr >= 0.5:
                        st.info(f"**High Diversity** ({ttr:.2%}): Good vocabulary variety. Typical of newspaper articles, blogs.")
                    elif ttr >= 0.3:
                        st.warning(f"**Moderate Diversity** ({ttr:.2%}): Some repetition. Typical of conversational text, social media.")
                    else:
                        st.error(f"**Low Diversity** ({ttr:.2%}): High repetition. Typical of technical documents, repetitive content.")
                    
                    # Formula
                    with st.expander("See calculation"):
                        st.markdown(f"""
                        ```
                        TTR = Types / Tokens
                        TTR = {num_types} / {num_tokens}
                        TTR = {ttr:.4f}
                        ```
                        """)
        
        else:
            # Text input
            text_input = st.text_area(
                "Paste your text here:",
                height=200,
                placeholder="Enter or paste text to analyze..."
            )
            
            if st.button("Analyze Text", type="primary"):
                if text_input.strip():
                    # Simple tokenization (split by whitespace and punctuation)
                    import re
                    tokens = re.findall(r'\b\w+\b', text_input.lower())
                    types = set(tokens)
                    
                    num_types = len(types)
                    num_tokens = len(tokens)
                    ttr = num_types / num_tokens if num_tokens > 0 else 0
                    
                    # Display results
                    st.markdown("### Results")
                    
                    res_col1, res_col2, res_col3 = st.columns(3)
                    
                    with res_col1:
                        st.metric("Types (Unique)", f"{num_types}")
                    
                    with res_col2:
                        st.metric("Tokens (Total)", f"{num_tokens}")
                    
                    with res_col3:
                        st.metric("TTR", f"{ttr:.4f}")
                    
                    # Visual indicator
                    st.progress(ttr, text=f"Lexical Diversity: {ttr:.2%}")
                    
                    # Interpretation
                    st.markdown("### Interpretation")
                    if ttr >= 0.7:
                        st.success(f"**Very High Diversity** ({ttr:.2%}): Rich vocabulary, low repetition.")
                    elif ttr >= 0.5:
                        st.info(f"**High Diversity** ({ttr:.2%}): Good vocabulary variety.")
                    elif ttr >= 0.3:
                        st.warning(f"**Moderate Diversity** ({ttr:.2%}): Some repetition.")
                    else:
                        st.error(f"**Low Diversity** ({ttr:.2%}): High repetition.")
                    
                    # Show sample of types
                    with st.expander("View unique words (Types)"):
                        st.write(", ".join(sorted(list(types))[:50]))
                        if len(types) > 50:
                            st.caption(f"... and {len(types) - 50} more")
                else:
                    st.warning("Please enter some text to analyze.")

# === Footer ===
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("""
This app helps with R text mining:
- **Search** R functions with autocomplete
- **Explore** packages and their functions  
- **Calculate** TF-IDF and Type-Token Ratio

Developed by Mathilde and Claude.""")