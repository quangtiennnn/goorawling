import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools import google_crawl

st.title("CSV Import and Row Selection")

# 1. File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Select row range (leave default for all rows):")
    start_row = st.number_input("Start row (0-based)", min_value=0, max_value=len(df)-1, value=0)
    end_row = st.number_input("End row (exclusive)", min_value=start_row+1, max_value=len(df), value=len(df))
    df_selected = df.iloc[start_row:end_row]
    st.dataframe(df_selected)

    # Multi-thread input
    thread_number = st.number_input("multi-thread_number", min_value=1, value=2)
    st.write(f"Selected multi-thread_number: {thread_number}")

    # Run crawl when button is pressed
    if st.button("Start Crawling"):
        st.write("Crawling started...")
        results = []
        def crawl_row(row):
            google_crawl(row['restaurant_id'], row['restaurant_link'])
            return row['restaurant_id']
        with ThreadPoolExecutor(max_workers=thread_number) as executor:
            futures = [executor.submit(crawl_row, row) for _, row in df_selected.iterrows()]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    st.success(f"Crawled: {result}")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.write("Crawling finished.")
else:
    st.info("Please upload a CSV file to begin.")