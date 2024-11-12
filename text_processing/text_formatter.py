from pdf_processing.ocr_processor import OCRProcessor
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class TextFormatter:
    def __init__(self, page_data):
        """
        Constructor for TextFormatter class that initializes the page data
        :param page_data: List of tuples containing image paths and extracted text for each page
        """
        self.page_data = page_data

    def format_extracted_data(self) -> list[str]:
        """
        Formats the extracted text and image text into a list of strings
        :return: List of formatted strings
        """
        formatted_results = []
        for i, (image_paths, extracted_text) in enumerate(self.page_data):
            formatted_page_text = f"<pagenumber>{i + 1}</pagenumber>\n<pagecontent>{extracted_text.strip()}</pagecontent>\n"

            for image_path in image_paths:
                image_text = OCRProcessor.extract_text_from_image(image_path)
                formatted_page_text += f"<imagecontent>{image_text}</imagecontent>\n"

            formatted_results.append(formatted_page_text)
        return formatted_results
