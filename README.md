# ATF OCR

A simple Tkinter GUI tool for performing OCR on PDF files and renaming them based on detected IDs.

## Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (binary installed and in your PATH)
- [Poppler](https://poppler.freedesktop.org/) utilities for PDF rendering
- Python packages listed in `requirements.txt`

## Installation

1. Install Tesseract and Poppler for your operating system.
   - On Windows you can use the `lib` binaries included in this repository.
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script and use the GUI to select PDF files and an output folder:

```bash
python src/main.py
```

The application will perform OCR on each PDF, search for known ID patterns and copy the files to the output folder using the detected ID as the new filename. Files without an ID are renamed with a `not_found` prefix.

## Development notes

- Update `pytesseract.pytesseract.tesseract_cmd` and the Poppler path in `src/main.py` if Tesseract or Poppler are installed elsewhere.
- Regex patterns for IDs can be modified in `src/main.py`.


