import os
import dotenv
import warnings
import streamlit as st

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from text_processing.preprocessing import preprocess
from langchain.vectorstores import FAISS
from collections import Counter


dotenv.load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH")


class QAChain:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.prompt_template = """
            Your name: "بالعربي"
            Your role: تقديم إجابات مفصلة على الأسئلة بناءً على السياق المقدم باللغة العربية فقط.

            Guidelines:
            - إذا كانت الإجابة مفقودة من السياق: فلا تجب إلا بـ "الإجابة غير موجودة في السياق". قلها باللغة العربية
            - يجب عليك الرد باللغة العربية.
            - لو المستخدم قام بتحيتك قم برد التحية بطريقه لطيفة.
            Prompt Structure:
            Context:
            {context}
        """.strip()
        self.chain = self._create_documents_chain()

    def _preapare_model(self) -> ChatGoogleGenerativeAI:
        """Load the conversational chain for question answering."""
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY
        )
        return model

    def _create_documents_chain(self):
        llm = self._preapare_model()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_template),
                ("human", "{input}"),
            ]
        )
        qa = create_stuff_documents_chain(llm, prompt)
        return qa

    def answer_question(self, user_question, session_key):
        """Answer the user's question based on the context, incorporating history."""
        try:
            chat_history = st.session_state[session_key].get("chat_history", [])

            history_text = "\n".join(
                [
                    f"User: {entry['question']}\nAI: {entry['answer']}"
                    for entry in chat_history
                ]
            )
            full_prompt = f"{self.prompt_template}\n\nChat History:\n{history_text}\n\nUser: {user_question}"

            # Load and configure the FAISS vector store
            db_vector = FAISS.load_local(
                FAISS_INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True
            )
            retriever = db_vector.as_retriever(search_kwargs={"k": 9})
            retrieval_chain = create_retrieval_chain(retriever, self.chain)
            result = retrieval_chain.invoke({"input": preprocess(full_prompt)})
            content = result.get("answer")
            page_numbers = [doc.dict()["metadata"]["page"] for doc in result["context"]]
            page_counts = Counter(page_numbers)

            most_common_page = (
                page_counts.most_common(1)[0][0]
                if page_counts
                else page_numbers[0] if page_numbers else None
            )

            return {
                "content": content,
                "page": (-1 if "غير موجودة" in content else page_numbers[0] + 1),
            }
        except Exception as e:
            print(f"Error answering question: {e}")
            return {
                "content": "Error occurred while processing the question.",
                "page": -1,
            }
