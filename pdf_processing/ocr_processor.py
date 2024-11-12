import cv2
import pytesseract
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class OCRProcessor:
    @staticmethod
    def extract_text_from_image(image_path):
        """Extract text from an image using Tesseract OCR."""
        try:
            img_cv = cv2.imread(image_path)
            arabic_text = pytesseract.image_to_string(img_cv, lang="ara")
            return arabic_text
        except Exception as e:
            print(f"Error extracting text from image {image_path}: {e}")
            return ""
