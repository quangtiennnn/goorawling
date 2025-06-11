# goorawling
<p align="center">
  <img src="data/logo.png" alt="Goorawling Logo" width="200"/>
  </p>

<p align="center">
    <span style="font-size:2em;">
        <span style="color:#4285F4;">G</span><span style="color:#EA4335;">o</span><span style="color:#FBBC05;">o</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">l</span><span style="color:#EA4335;">e</span>
        <strong><span style="color:#EA4335;"> Crawling ???</span></strong>
    </span>
</p>

# Goorawling Streamlit App

A Streamlit web app for uploading CSV files, selecting row ranges, and running multi-threaded crawling tasks.

## Features

- Upload a CSV file and preview its contents
- Select a range of rows to process
- Set the number of threads for crawling
- Run a custom crawl function on selected rows

## Installation

1. Clone this repository:
    ```
    git clone https://github.com/quangtiennnn/goorawling.git
    cd goorawling
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

Run the Streamlit app:
```
streamlit run setup.py
```

Upload your CSV file and follow the on-screen instructions.

## Dependencies

- streamlit
- pandas
- selenium