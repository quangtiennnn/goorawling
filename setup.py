import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools import *

# GLOBAL VARIABLES
current_proxy = None



st.title("CSV Import and Row Selection")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Select row range (leave default for all rows):")
    start_row = st.number_input("Start row (0-based)", min_value=0, max_value=len(df)-1, value=0)
    end_row = st.number_input("End row (exclusive)", min_value=start_row+1, max_value=len(df), value=len(df))
    df_selected = df.iloc[start_row:end_row].reset_index(drop=True)
    st.dataframe(df_selected)


    thread_number = st.number_input("Multi-thread number", min_value=1, value=2)
    st.write(f"Selected multi-thread number: {thread_number}")

    crawl_images = st.checkbox("Crawl Images", value=True)
    crawl_reviews = st.checkbox("Crawl Reviews", value=False)

    if st.button("Start Crawling"):
        st.write("Crawling started...")
        results = []
        progress = st.progress(0)
        total = len(df_selected)

        def crawl_row(row):
            global current_proxy
            proxy = current_proxy
            result = google_crawl(
                str(row['restaurant_id']),
                row['restaurant_link'],
                proxy=proxy,
                images=crawl_images,
                reviews=crawl_reviews
            )
            # If google_crawl returns 0 (afterClick_url == current_url), try with a new proxy
            if result == 0:
                print('Result = 0! Running to find a new proxy...')
                proxy = get_first_working_proxy_from_url()
                current_proxy = proxy  # Update the global proxy
                result = google_crawl(
                    str(row['restaurant_id']),
                    row['restaurant_link'],
                    proxy=proxy,
                    images=crawl_images,
                    reviews=crawl_reviews
                )
            return row['restaurant_id']

        with ThreadPoolExecutor(max_workers=thread_number) as executor:
            futures = {executor.submit(crawl_row, row): idx for idx, (_, row) in enumerate(df_selected.iterrows())}
            for i, future in enumerate(as_completed(futures)):
                idx = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    st.success(f"Crawled: {result}")
                except Exception as e:
                    st.error(f"Error: {e}")
                progress.progress((i + 1) / total)
        st.write("Crawling finished.")
else:
    st.info("Please upload a CSV file to begin.")