import streamlit as st
from design.main_ui import PDFChatbotUI
import os
import dotenv

dotenv.load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
chatbot_ui = PDFChatbotUI(google_api_key)
chatbot_ui.setup_ui()
