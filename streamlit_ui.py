import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
import csv as csv_module

CSV_QUOTING = csv_module.QUOTE_ALL

# Set page configuration
st.set_page_config(
    page_title="HPO Sentence Annotation Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load the CSV file
@st.cache_data
def load_data(file_path="./data/hpo_diverse_sentences_0-50.csv"):
    try:
        if not os.path.exists(file_path):
            st.error(f"File not found: {file_path}")
            return None
        return pd.read_csv(file_path, quoting=CSV_QUOTING)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


# Function to download dataframe as CSV
def get_csv_download_link(df, filename="./data/annotations.csv"):
    csv_content = df.to_csv(index=False, quoting=CSV_QUOTING)
    b64 = base64.b64encode(csv_content.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href


# Main app
def main():
    st.title("HPO Sentence Annotation Tool")

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    annotator_name = st.sidebar.text_input("Enter your name:", key="annotator_name")

    # Initialize session state
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    if 'annotations' not in st.session_state:
        st.session_state.annotations = None

    if 'data' not in st.session_state:
        st.session_state.data = None

    # Load data automatically
    if st.session_state.data is None:
        data = load_data()
        if data is not None:
            st.session_state.data = data

            st.session_state.annotations = pd.DataFrame({
                'annotator': [annotator_name] * len(data),
                'hpo_label': data['hpo_label'].tolist(),
                'hpo_id': data['hpo_id'].tolist(),
                'sentence': data['sentence'].tolist(),
                'span': data['span'].tolist(),
                'is_correct': [None] * len(data),
                'timestamp': [None] * len(data)
            })

            st.success("Data loaded successfully! Ready for annotation.")

    # Main annotation interface
    if st.session_state.data is not None and annotator_name:
        data = st.session_state.data
        annotations = st.session_state.annotations
        idx = st.session_state.current_index
        current_row = data.iloc[idx]

        st.progress(idx / len(data))
        st.write(f"Annotating {idx + 1} of {len(data)}")

        # Display HPO term
        st.subheader("HPO Term")
        st.markdown(f"<span style='font-size: 16px;'><b>{current_row['hpo_label']}</b> ({current_row['hpo_id']})</span>", unsafe_allow_html=True)

        st.subheader("Sentence")
        st.write(current_row['sentence'])

        # st.subheader("Annotation")
        st.write("Is this sentence relevant with the HPO term?")

        col_yes, col_no = st.columns([1, 1])
        with col_yes:
            if st.button("✅ Yes", key="yes_button"):
                annotations.loc[idx, 'is_correct'] = 1
                annotations.loc[idx, 'timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                annotations.loc[idx, 'annotator'] = annotator_name
                if idx < len(data) - 1:
                    st.session_state.current_index += 1
                st.rerun()

        with col_no:
            if st.button("❌ No", key="no_button"):
                annotations.loc[idx, 'is_correct'] = 0
                annotations.loc[idx, 'timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                annotations.loc[idx, 'annotator'] = annotator_name
                if idx < len(data) - 1:
                    st.session_state.current_index += 1
                st.rerun()

        # Previous button below
        if st.button("⬅️ Previous", key="prev_button"):
            if idx > 0:
                st.session_state.current_index -= 1
            st.rerun()

        if st.button("Save Annotations"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hpo_annotations_{annotator_name}_{timestamp}.csv"
            st.markdown(get_csv_download_link(annotations, filename), unsafe_allow_html=True)
            st.success("Annotations ready for download!")

        completed = annotations['is_correct'].notnull().sum()
        st.write(f"Completed: {completed}/{len(data)} annotations")

        if st.checkbox("Show all annotations"):
            st.dataframe(annotations)

    else:
        if not annotator_name:
            st.warning("Please enter your name in the sidebar to begin annotation.")


if __name__ == "__main__":
    main()
