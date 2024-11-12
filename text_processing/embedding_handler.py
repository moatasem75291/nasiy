import os
import dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from text_processing.preprocessing import preprocess
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

dotenv.load_dotenv()
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH")


class EmbeddingHandler:
    """
    Handles the creation of a vector store from text chunks.
    """

    def __init__(self, embeddings):
        self.embeddings = embeddings

    def get_text_chunks(self, pdf_path) -> list[Document]:
        """
        Get text chunks from a PDF file.
        :params
        pdf_path:

        :return

        """
        loader = PyPDFLoader(pdf_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, chunk_overlap=40
        )
        pages = loader.load_and_split(text_splitter)

        docs = []
        for page in pages:
            page = page.dict()
            page_content = preprocess(page["page_content"])
            docs.append(Document(page_content, metadata=page["metadata"]))
        return docs

    def get_vector_store(self, text_chunks) -> None:
        """Create a vector store from text chunks and save it locally."""
        try:
            vector_store = FAISS.from_documents(text_chunks, embedding=self.embeddings)
            vector_store.save_local(FAISS_INDEX_PATH)

        except Exception as e:
            print(f"Error creating vector store: {e}")
