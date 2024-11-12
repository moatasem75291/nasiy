import os
import google.generativeai as genai
import dotenv
import textwrap
from IPython.display import Markdown

dotenv.load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY_SUMMARIZATION"])


class FileSummarizer:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def to_markdown(self, text: str) -> str:
        """Convert text to markdown format."""
        text = text.replace("•", "  *")
        # indented_text = textwrap.indent(text, "> ", predicate=lambda _: True)
        return f"```markdown\n{text}\n```"

    def upload_and_summarize(self, pdf_path):
        """Upload PDF, generate a summary in Arabic, and print the summary."""
        try:
            pdf_file = genai.upload_file(pdf_path)
            prompt = """
            - يرجى تلخيص محتوى ملف PDF المرفق باللغة العربية. يجب أن يكون الملخص موجزا ويغطي النقاط الرئيسية في الوثيقة.
            - لازم ترد بالعربي فقط.
            """
            response = self.model.generate_content([prompt, pdf_file])
            text = self.to_markdown(response.text)
            return text
        except Exception as e:
            print(f"Error summarizing file: {e}")
