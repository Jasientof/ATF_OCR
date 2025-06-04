# ATF OCR

A simple Tkinter GUI tool for performing OCR on PDF files and renaming them based on detected IDs.

## Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler](https://poppler.freedesktop.org/) utilities
- Python packages listed in `requirements.txt`

## Installation

1. Install Tesseract and Poppler for your operating system. On Windows you can use the binaries in `lib` or install the official packages.
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

On first launch the program attempts to automatically locate the Tesseract and Poppler binaries. If they cannot be found you will be prompted to provide their locations. Paths and the regex patterns used for ID detection are stored in `src/config.json` and can also be edited through the **File → Settings** menu.

For convenience you can create standalone executables with [PyInstaller](https://www.pyinstaller.org/):

```bash
pyinstaller --noconsole --onefile src/main.py
```

## Development notes

All user configurable options are stored in `src/config.json`. If you need additional patterns or custom paths you can edit this file directly or use the Settings menu while the program is running.


