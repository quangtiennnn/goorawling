import streamlit as st
import pandas as pd

df = pd.read_csv("data/tripadvisor_restaurant/restaurant_links.csv")
df  = df[0:4]   # Limiting to 4 rows for demonstration


st.dataframe(df)

for idx, row in df.iterrows():
    with st.form(key=f"form_{idx}"):
        user_input = st.text_input(f"Input for {row['restaurant_id']}", key=f"input_{idx}")
        submit = st.form_submit_button("Submit")
        if submit:
            st.success(f"Received input for {row['restaurant_id']}: {user_input}")