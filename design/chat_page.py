import os
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from record_and_transcribe import AudioTranscriber


class ChatPage:
    def __init__(self, session_key):
        self.session_key = session_key
        self.qa_chain = st.session_state.get(session_key, {}).get("qa_chain", None)

        if self.qa_chain is None:
            st.error("Error: QA chain is not initialized. Please upload a PDF first.")

    def generate_response(self, user_input):
        """Generate response for the user input using the QA chain."""
        if not self.qa_chain:
            return {
                "content": "Sorry, I can't process your request right now.",
                "page": -1,
            }

        data_dict = self.qa_chain.answer_question(user_input, self.session_key)
        response = {
            "content": data_dict["content"],
            "page": data_dict["page"],
        }
        return response

    def display_chat_history(self):
        """Display the chat history for the current session."""
        chat_history = st.session_state[self.session_key].get("chat_history", [])

        for i, entry in enumerate(chat_history):
            user_key = f"user_{i}_{len(chat_history)}"
            bot_key = f"bot_{i}_{len(chat_history)}"

            message(
                entry["question"],
                is_user=True,
                key=user_key,
                avatar_style="initials",
                seed="QB",
            )
            message(entry["answer"], key=bot_key, avatar_style="initials", seed="AI")

    def handle_audio_input(self):
        """Process and transcribe audio input, if available, and display it in a text input."""
        audio_value = st.audio_input("Record your question:")
        if audio_value:
            audio_path = os.path.join("temp", "user_question.wav")
            with open(audio_path, "wb") as f:
                f.write(audio_value.getbuffer())
            transcriber = AudioTranscriber()
            transcribed_text = transcriber.transcribe_audio(audio_path)
            st.session_state["transcribed_text"] = transcribed_text  # Store for editing
            return transcribed_text

    def show_chat_page(self):
        """Render the chat page UI, including input handling and chat display."""
        colored_header(label="", description="", color_name="gray-30")
        st.session_state["transcribed_text"] = ""

        user_input = st.chat_input("Type or say something:")

        if user_input:
            response = self.generate_response(user_input)
            st.session_state[self.session_key]["chat_history"].append(
                {
                    "question": user_input,
                    "answer": response["content"],
                    "page": response["page"],
                }
            )
        transcribed_text = self.handle_audio_input()
        if transcribed_text:
            response = self.generate_response(transcribed_text)
            st.session_state[self.session_key]["chat_history"].append(
                {
                    "question": transcribed_text,
                    "answer": response["content"],
                    "page": response["page"],
                }
            )

        st.session_state["transcribed_text"] = ""
        self.display_chat_history()
