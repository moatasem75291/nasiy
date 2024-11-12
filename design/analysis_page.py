import streamlit as st
from analysis.pdf_analysis import perform_analysis
from summarization.summary import FileSummarizer


def show_analysis_page(session_key):
    st.title("PDF Analysis")
    summarizer = FileSummarizer()
    summary = summarizer.upload_and_summarize(
        st.session_state[session_key]["file_path"]
    )
    st.write(summary)

    if st.session_state[session_key]["text_chunks"]:
        statistics = perform_analysis(
            st.session_state[session_key]["full_text"]
        )
        # st.write("### Word Cloud")
        # st.pyplot(wordcloud)
        st.write("### Top Word Frequencies")
        st.dataframe(statistics)

    else:
        st.warning("No text data available for analysis.")
