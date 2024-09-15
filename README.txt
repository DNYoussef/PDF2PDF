# DocuRefine

DocuRefine is a powerful document processing tool designed to transform poorly formatted or scanned documents into searchable, editable PDFs while preserving the original layout. The system handles both PDFs and image inputs, processes them page by page, and outputs a refined PDF document.

## Key Features

1. PDF splitting and image processing
2. OCR (Optical Character Recognition) for text extraction
3. Layout analysis
4. Text-to-LaTeX conversion
5. Image comparison for quality control
6. PDF reconstruction
7. User management and authentication

## Tech Stack

- Python 3.8+
- PyPDF2 (now updated to PyPDF4 or pypdf)
- Tesseract (via pytesseract)
- Layout Parser
- Hugging Face Transformers
- scikit-image
- OpenCV (cv2)
- Celery
- Redis
- Flask
- SQLAlchemy
- Prometheus (for monitoring)

## Installation

1. Clone the repository:
https://github.com/yourusername/docurefine.git cd docurefine


2. Install dependencies:
pip install -r requirements.txt


3. Set up environment variables (create a .env file in the project root):
FLASK_APP=src/app.py FLASK_ENV=development

## Usage

1. Start the Flask application:
flask run

2. Start Celery worker:
celery -A config.celery_config worker --loglevel=info

3. Start Flower (Celery monitoring tool):
celery -A config.celery_config flower

4. (Optional) If using Docker:
docker-compose up

For detailed API usage, refer to the [API documentation](docs/API.md).

Information Flow:

```
+----------------+     +----------------+     +----------------+
|   Input File   |     |  Page Splitter |     |   OCR Engine   |
| (PDF or Images)|---->| (PyPDF2/OpenCV)|---->|  (Tesseract)   |
+----------------+     +----------------+     +----------------+
                                                      |
                                                      v
+----------------+     +----------------+     +----------------+
|  PDF Merger    |     | LaTeX Renderer |     | Layout Analyzer|
| (PyPDF2)       |<----| (pdflatex)     |<----| (LayoutParser) |
+----------------+     +----------------+     +----------------+
        ^                      ^                      |
        |                      |                      v
+----------------+     +----------------+     +----------------+
|   Final PDF    |     |Image Comparator|     | LaTeX Converter|
|                |     | (scikit-image) |---->| (Transformers) |
+----------------+     +----------------+     +----------------+
```

File Structure:

```
docurefine/
│
├── src/
│   ├── __init__.py
│   ├── pdf_utils.py        # PDF splitting and merging functions
│   ├── ocr.py              # OCR functions
│   ├── layout_analysis.py  # Layout analysis functions
│   ├── latex_converter.py  # Text to LaTeX conversion
│   ├── image_comparison.py # Image comparison functions
│   ├── celery_tasks.py     # Celery task definitions
│   └── main.py             # Main script orchestrating the process
│
├── tests/
│   ├── __init__.py
│   ├── test_pdf_utils.py
│   ├── test_ocr.py
│   ├── test_layout_analysis.py
│   ├── test_latex_converter.py
│   └── test_image_comparison.py
│
├── models/
│   └── latex_converter/    # Fine-tuned model for LaTeX conversion
│
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration settings
│
├── docs/
│   ├── README.md
│   └── API.md
│
├── requirements.txt
├── setup.py
└── .gitignore
```
## Testing

Run the tests using:
python -m unittest discover tests


## Configuration

- Application configuration: `config/config.py`
- Celery configuration: `config/celery_config.py`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[Include license information]

## Acknowledgments

- [List any libraries, tools, or resources you want to acknowledge]
T
