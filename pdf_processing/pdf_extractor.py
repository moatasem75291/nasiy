import os
from spire.pdf import PdfDocument, PdfImageHelper
from PyPDF2 import PdfReader
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class PDFExtractor:
    """
    Extract images and text from a PDF file.
    """

    def __init__(self, pdf_path, output_directory):
        self.pdf_path = pdf_path
        self.output_directory = output_directory

    def extract_images_and_text(self) -> list[tuple[list[str], str]]:
        """
        Extract images and text from a PDF file. Returns a list of tuples
        where each tuple contains a list of image paths and the extracted text
        from a page.
        """
        page_data = []
        try:
            doc = PdfDocument()
            doc.LoadFromFile(self.pdf_path)
            pdf_reader = PdfReader(self.pdf_path)
            image_helper = PdfImageHelper()

            for i in range(doc.Pages.Count):
                page = doc.Pages.get_Item(i)
                images_info = image_helper.GetImagesInfo(page)
                extracted_text = pdf_reader.pages[i].extract_text()
                image_paths = []

                for j, image_info in enumerate(images_info):
                    image_file_name = os.path.join(
                        self.output_directory, f"Image-{i}-{j}.png"
                    )
                    image_info.Image.Save(image_file_name)
                    image_paths.append(image_file_name)

                page_data.append((image_paths, extracted_text))

            doc.Close()
        except Exception as e:
            print(f"Error extracting images and text: {e}")
        return page_data
