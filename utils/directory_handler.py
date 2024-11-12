import os


def create_output_directory(pdf_path) -> str:
    """Create an output directory based on the PDF file name."""
    output_dir = os.path.join(
        os.path.dirname(pdf_path), pdf_path.split("\\")[-1].replace(".pdf", "")
    )
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
