import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from text_processing.embedding_handler import EmbeddingHandler
from design.chat_page import ChatPage
from design.analysis_page import show_analysis_page
from design.about_page import show_about_page
from chatbot.qa_chain import QAChain


class PDFChatbotUI:
    def __init__(self, google_api_key):
        self.google_api_key = google_api_key
        self.page_title = "نَصّي"
        self.logo = "نلخص، نفهم، ونحكي لك الجواب"
        self._initialize_session_state()
        st.set_page_config(page_title=self.page_title, layout="wide")

    def _initialize_session_state(self):
        if "user_responses" not in st.session_state:
            st.session_state["user_responses"] = ["ازيك؟"]
        if "bot_responses" not in st.session_state:
            st.session_state["bot_responses"] = ["أهلاً بك! كيف يمكنني مساعدتك؟"]
        if "transcribed_text" not in st.session_state:
            st.session_state["transcribed_text"] = ""

    def load_embedding_handler(self):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=self.google_api_key
        )
        return EmbeddingHandler(embeddings)

    def setup_ui(self):
        st.title(f":violet[{self.page_title}]")
        st.sidebar.title(self.logo)

        page_selection = st.sidebar.radio(
            "Navigate", ["About", "Chat with PDF", "Analysis"]
        )
        uploaded_file = st.sidebar.file_uploader("Upload a PDF", type="pdf")
        if uploaded_file:
            session_key = f"file_{uploaded_file.name}"
            self._process_uploaded_file(uploaded_file, session_key, page_selection)
        else:
            if page_selection == "About":
                show_about_page(self.logo)
            else:
                st.info("Please upload a PDF to continue.")

    def _process_uploaded_file(self, uploaded_file, session_key, page_selection):
        if session_key not in st.session_state:
            st.session_state[session_key] = {
                "chat_history": [],
                "text_chunks": None,
                "total_pages": 0,
                "qa_chain": None,
                "embedding_handler": self.load_embedding_handler(),
                "full_text": "",
                "file_path": "",
            }
            temp_pdf_path = os.path.join("temp", uploaded_file.name)
            st.session_state[session_key]["file_path"] = temp_pdf_path
            os.makedirs("temp", exist_ok=True)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.read())
            self._initialize_text_processing(session_key, temp_pdf_path)

        if page_selection == "Analysis":
            show_analysis_page(session_key)
        elif page_selection == "Chat with PDF":
            chat_page = ChatPage(session_key)
            chat_page.show_chat_page()
        elif page_selection == "About":
            show_about_page(self.logo)

    def _initialize_text_processing(self, session_key, pdf_path):
        embedding_handler = st.session_state[session_key]["embedding_handler"]
        text_chunks = embedding_handler.get_text_chunks(pdf_path)
        embedding_handler.get_vector_store(text_chunks)

        st.session_state[session_key]["text_chunks"] = text_chunks
        st.session_state[session_key]["total_pages"] = len(text_chunks)
        st.session_state[session_key]["full_text"] = " ".join(
            [doc.dict()["page_content"] for doc in text_chunks]
        )
        st.session_state[session_key]["qa_chain"] = QAChain(
            embedding_handler.embeddings
        )
