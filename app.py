import streamlit as st
import pandas as pd
import plotly.express as px
import uuid

# Set page configuration for a wide layout and custom theme
st.set_page_config(
    page_title="Options Position Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 10px;
    }
    /* Header styling */
    h1 {
        color: #1e3a8a;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
    }
    /* Subheader styling */
    h2 {
        color: #3b82f6;
        font-family: 'Arial', sans-serif;
    }
    /* File uploader styling */
    .stFileUploader > div > div {
        border: 2px dashed #3b82f6;
        border-radius: 8px;
        padding: 10px;
        background-color: #eff6ff;
    }
    /* Button styling */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #1e40af;
    }
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e3a8a;
        color: white;
    }
    .css-1d391kg h1, .css-1d391kg h2 {
        color: white !important;
    }
    /* Info box styling */
    .stInfo {
        background-color: #dbeafe;
        border-left: 5px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Theme toggle in sidebar
st.sidebar.title("Options Analyzer")
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])

# Apply theme-specific styling
if theme == "Dark":
    st.markdown("""
    <style>
        .main {
            background-color: #1f2937;
            color: #f3f4f6;
        }
        h1 {
            color: #60a5fa;
        }
        h2 {
            color: #93c5fd;
        }
        .stFileUploader > div > div {
            background-color: #374151;
            border-color: #60a5fa;
        }
        .stInfo {
            background-color: #374151;
            border-left-color: #60a5fa;
        }
    </style>
    """, unsafe_allow_html=True)

# Main title with emoji and animation
st.markdown("""
<h1>
    <span style='display: inline-flex; align-items: center;'>
        📊 Options Position Analyzer
        <span style='font-size: 0.5em; margin-left: 10px; color: #3b82f6;'>v1.0</span>
    </span>
</h1>
""", unsafe_allow_html=True)

# File uploader with enhanced instructions
st.markdown("### Upload Your Data")
uploaded_file = st.file_uploader(
    "Drop your POS CSV file here or click to browse",
    type=["csv"],
    help="Upload a CSV file containing options position data with columns: UserID, Symbol, Product, Buy Qty, Sell Qty."
)

if uploaded_file is not None:
    # Load CSV
    df = pd.read_csv(uploaded_file)
    df = df[df["Product"] == "MIS"]

    # Identify option type
    df['OptionType'] = df['Symbol'].apply(
        lambda x: 'Call' if 'CE' in str(x) else ('Put' if 'PE' in str(x) else 'Other')
    )

    # Assign lot size based on symbol
    def get_lot_size(symbol):
        symbol = str(symbol).upper()
        if "NIFTY" in symbol:
            return 75
        elif "SENSEX" in symbol:
            return 20
        else:
            return 1  # default if neither NIFTY nor SENSEX

    df['LotSize'] = df['Symbol'].apply(get_lot_size)

    # Group and aggregate
    summary = (
        df.groupby(['UserID', 'OptionType'], as_index=False)
          .agg({'Buy Qty': 'sum', 'Sell Qty': 'sum', 'LotSize': 'max'})
    )

    # Calculate difference and lots
    summary['difference'] = summary['Buy Qty'] - summary['Sell Qty']
    summary['lots'] = summary['difference'] / summary['LotSize']

    # Tabs for different views
    tab2, tab1 = st.tabs([ "📊 Summary","📋 Raw Data"])

    with tab1:
        st.subheader("Raw Data")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Summary (Aggregated by User & Option Type)")
        st.dataframe(summary, use_container_width=True)

        # Download button
        csv = summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Summary as CSV",
            data=csv,
            file_name="summary.csv",
            mime="text/csv",
            key=f"download_{uuid.uuid4()}"  # Unique key for button
        )

    
    st.sidebar.subheader("Filter Data")
    users = df['UserID'].unique().tolist()
    selected_user = st.sidebar.selectbox("Select UserID", ["All"] + users)
    if selected_user != "All":
        filtered_summary = summary[summary['UserID'] == selected_user]
        st.subheader(f"Filtered Summary for User: {selected_user}")
        st.dataframe(filtered_summary, use_container_width=True)

        # Download filtered summary
        filtered_csv = filtered_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download Filtered Summary ({selected_user})",
            data=filtered_csv,
            file_name=f"summary_{selected_user}.csv",
            mime="text/csv",
            key=f"download_filtered_{uuid.uuid4()}"
        )

else:
    st.info("👆 Upload a POS CSV file to start analyzing your options positions. Ensure your CSV includes UserID, Symbol, Product, Buy Qty, and Sell Qty columns.")

# Footer
st.markdown("""
---
<div style='text-align: center; color: #6b7280;'>
    Powered by Streamlit | © 2025 Options Position Analyzer
</div>
""", unsafe_allow_html=True)