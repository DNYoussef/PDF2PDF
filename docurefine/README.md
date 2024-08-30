# DocuRefine

DocuRefine is a tool for transforming poorly formatted or scanned documents into searchable, editable PDFs while preserving the original layout.

## Features

- PDF splitting and image processing
- OCR for text extraction
- Layout analysis
- Text-to-LaTeX conversion
- Image comparison for quality control
- PDF reconstruction
- User authentication and file management

## Tech Stack

- Python 3.8+
- Flask (Web framework)
- Celery (Task queue)
- Redis (Message broker)
- PyPDF2 (PDF manipulation)
- Tesseract (OCR)
- Layout Parser (Document layout analysis)
- Hugging Face Transformers (Text-to-LaTeX conversion)
- scikit-image (Image comparison)
- OpenCV (Image preprocessing)

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/docurefine.git
   cd docurefine
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` as needed

4. Initialize the database:
   ```
   flask db upgrade
   ```

5. Start the Celery worker:
   ```
   celery -A celery_worker worker --loglevel=info
   ```

6. Start the Flask development server:
   ```
   flask run
   ```

## Usage

Refer to the [User Guide](docs/USER_GUIDE.md) for detailed usage instructions.

## API Documentation

API documentation can be found in the [API.md](docs/API.md) file.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.