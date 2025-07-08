import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
import csv

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
        return pd.read_csv(file_path, quoting=csv.QUOTE_ALL)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


# Function to download dataframe as CSV
def get_csv_download_link(df, filename="./data/annotations.csv"):
    csv_content = df.to_csv(index=False, quoting=csv.QUOTE_ALL)
    b64 = base64.b64encode(csv_content.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href


# Main app
def main():
    st.title("HPO Sentence Annotation Tool")

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Annotator name input
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

            # Initialize annotations dataframe with the same structure as input plus annotation column
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

        # Display progress
        st.progress((st.session_state.current_index) / len(data))
        st.write(f"Annotating {st.session_state.current_index + 1} of {len(data)}")

        # Display current sentence
        current_row = data.iloc[st.session_state.current_index]

        # Display HPO information
        # col1, col2 = st.columns(2)
        # with col1:
        #     st.subheader("HPO Term")
        #     st.write(f"**Label:** {current_row['hpo_label']}")
        #     st.write(f"**ID:** {current_row['hpo_id']}")
        st.subheader("HPO Term")
        st.markdown(f"<span style='font-size: 16px;'><b>{current_row['hpo_label']}</b> ({current_row['hpo_id']})</span>",
            unsafe_allow_html=True)

        # Display sentence and span
        st.subheader("Sentence")
        st.write(current_row['sentence'])
        #
        # st.subheader("Highlighted Span")
        # st.info(current_row['span'])

        # Annotation options
        st.subheader("Annotation")

        # Is the span correct?
        current_value = st.session_state.annotations.iloc[st.session_state.current_index]['is_correct']
        default_index = 0
        if current_value == 1:
            default_index = 0
        elif current_value == 0:
            default_index = 1

        is_correct = st.radio(
            "Is this sentence relevant with the HPO term?",
            ["Yes (1)", "No (0)"],
            index=default_index
        )

        # Convert radio button selection to binary value
        is_correct_value = 1 if is_correct == "Yes (1)" else 0

        # Navigation buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Previous", disabled=(st.session_state.current_index == 0)):
                # Save current annotation
                st.session_state.annotations.loc[st.session_state.current_index, 'is_correct'] = is_correct_value
                st.session_state.annotations.loc[st.session_state.current_index, 'timestamp'] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                st.session_state.annotations.loc[st.session_state.current_index, 'annotator'] = annotator_name

                # Go to previous sample
                st.session_state.current_index -= 1
                st.rerun()

        with col2:
            if st.button("Next", disabled=(st.session_state.current_index == len(data) - 1)):
                # Save current annotation
                st.session_state.annotations.loc[st.session_state.current_index, 'is_correct'] = is_correct_value
                st.session_state.annotations.loc[st.session_state.current_index, 'timestamp'] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                st.session_state.annotations.loc[st.session_state.current_index, 'annotator'] = annotator_name

                # Go to next sample
                st.session_state.current_index += 1
                st.rerun()

        with col3:
            if st.button("Save Annotations"):
                # Save current annotation
                st.session_state.annotations.loc[st.session_state.current_index, 'is_correct'] = is_correct_value
                st.session_state.annotations.loc[st.session_state.current_index, 'timestamp'] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                st.session_state.annotations.loc[st.session_state.current_index, 'annotator'] = annotator_name

                # Generate download link
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"hpo_annotations_{annotator_name}_{timestamp}.csv"
                st.markdown(get_csv_download_link(st.session_state.annotations, filename), unsafe_allow_html=True)
                st.success("Annotations ready for download!")

        # Display annotation progress
        completed = st.session_state.annotations['is_correct'].notnull().sum()
        st.write(f"Completed: {completed}/{len(data)} annotations")

        # Display annotations table
        if st.checkbox("Show all annotations"):
            st.dataframe(st.session_state.annotations)

    else:
        if not annotator_name:
            st.warning("Please enter your name in the sidebar to begin annotation.")


if __name__ == "__main__":
    main()
