import os
import streamlit as st
import warnings
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header

from text_processing.embedding_handler import EmbeddingHandler
from chatbot.qa_chain import QAChain
from analysis.pdf_analysis import perform_analysis
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from record_and_transcribe import AudioRecorder, AudioTranscriber  # Import classes

warnings.filterwarnings("ignore", category=DeprecationWarning)


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
                self.show_about_page()
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
            }

            temp_pdf_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.read())

            self._initialize_text_processing(session_key, temp_pdf_path)
            st.sidebar.success(f"Uploaded: {uploaded_file.name}")

            self._initialize_session_state()

        if page_selection == "Analysis":
            self._show_analysis_page(session_key)
        elif page_selection == "Chat with PDF":
            self._show_chat_page(session_key)
        elif page_selection == "About":
            self.show_about_page()

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

    def _show_analysis_page(self, session_key):
        st.title("PDF Analysis")
        st.write("Below is a summary of the PDF content.")
        if st.session_state[session_key]["text_chunks"]:
            wordcloud, statistics, sentiment = perform_analysis(
                st.session_state[session_key]["full_text"]
            )
            st.write("### Word Cloud")
            st.pyplot(wordcloud)
            st.write("### Top Word Frequencies")
            st.dataframe(statistics)
            st.write("### Sentiment Analysis")
            st.write(f"Positive: {sentiment['pos'] * 100:.2f}%")
            st.write(f"Neutral: {sentiment['neu'] * 100:.2f}%")
            st.write(f"Negative: {sentiment['neg'] * 100:.2f}%")
            st.write(f"**Total Pages:** {st.session_state[session_key]['total_pages']}")
        else:
            st.warning("No text data available for analysis.")

    def _show_chat_page(self, session_key):
        st.title("Chat with PDF")
        colored_header(label="", description="", color_name="gray-30")
        self._display_chat_history()
        st.divider()

        audio_value = st.experimental_audio_input("Record your question:")

        if audio_value:
            audio_path = os.path.join("temp", "user_question.wav")
            with open(audio_path, "wb") as f:
                f.write(audio_value.getbuffer())

            transcriber = AudioTranscriber()
            st.session_state["transcribed_text"] = transcriber.transcribe_audio(
                audio_path
            )
        user_input = st.text_input(
            "You: ", st.session_state.get("transcribed_text", ""), key="input"
        )

        if st.button("Send"):
            if user_input:
                response = self._generate_response(session_key, user_input)
                st.session_state["user_responses"].append(user_input)
                st.session_state["bot_responses"].append(response)
                st.session_state["transcribed_text"] = ""

    def _generate_response(self, session_key, user_input):
        data_dict = st.session_state[session_key]["qa_chain"].answer_question(
            user_input
        )
        response = data_dict["content"]
        st.session_state[session_key]["chat_history"].append(
            {"question": user_input, "answer": response, "page": data_dict["page"]}
        )
        return response

    def _display_chat_history(self):
        for i in range(len(st.session_state["bot_responses"])):
            message(
                st.session_state["user_responses"][i],
                is_user=True,
                key=str(i) + "_user",
                avatar_style="initials",
                seed="QB",
            )
            message(
                st.session_state["bot_responses"][i],
                key=str(i),
                avatar_style="initials",
                seed="AI",
            )

    def show_about_page(self):
        st.title("مرحباً بكم في نَصّي!")
        st.write("**نلخص، نفهم، ونحكي لك الجواب**")

        st.subheader("رؤيتنا")
        st.write(
            "في موقع نَصّي، نسعى إلى تبسيط المعلومات وتسهيل الوصول إلى المعرفة بشكل مبتكر. "
            "هدفنا هو تمكين المستخدمين من فهم محتوى النصوص بشكل أعمق وسريع، من خلال أدوات تعتمد على الذكاء الاصطناعي."
        )

        st.subheader("ماذا نقدم؟")
        st.write(
            "يقدم موقع نَصّي حلولًا متكاملة لتحليل النصوص وتوفير إجابات دقيقة وملخصات وافية، "
            "لتلبية احتياجات المستخدمين في مختلف المجالات سواء كان ذلك في التعليم، البحث، أو الأعمال."
        )
