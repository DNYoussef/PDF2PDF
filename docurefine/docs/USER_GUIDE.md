# DocuRefine User Guide

DocuRefine is a tool for transforming poorly formatted or scanned documents into searchable, editable PDFs while preserving the original layout.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/docurefine.git
   cd docurefine
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy the `.env.example` file to `.env`
   - Update the values in `.env` as needed, especially:
     - `SECRET_KEY`: Set this to a random, secure string
     - `DATABASE_URL`: Set your database URL (default is SQLite)
     - `REDIS_URL`: Set your Redis URL (default is localhost)
     - `SENTRY_DSN`: Set this if you're using Sentry for error tracking

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Start the Redis server (if not already running)

7. Start the Celery worker:
   ```
   celery -A celery_worker worker --loglevel=info
   ```

8. Start the Flask development server:
   ```
   flask run
   ```

## Usage

### User Authentication

1. Register a new account:
   - Navigate to `/register`
   - Enter your desired username, email, and password
   - Click "Register"

2. Log in to your account:
   - Navigate to `/login`
   - Enter your username and password
   - Click "Login"

3. Log out:
   - Click the "Logout" link in the navigation menu

### Processing Documents

1. After logging in, you'll see the main page with a drag-and-drop area.

2. You can either:
   - Drag and drop files into the designated area
   - Click on the area to open a file selection dialog

3. Select one or more files to process. Supported formats are:
   - PDF
   - PNG, JPG, JPEG
   - DOCX
   - HTML

4. Once files are added, they will appear in a list below the drag-and-drop area.

5. You can remove files from the list by clicking the "×" next to each file name.

6. When you're ready to process the files, click the "Start Processing" button.

7. A progress bar will appear, showing the upload progress.

8. After the upload is complete, you'll see status updates as the files are processed.

9. Once processing is complete, you'll be prompted to download the result.

### File Management

1. View your processed files:
   - Navigate to the `/files` page
   - You'll see a list of all your processed documents

2. Download a processed file:
   - On the `/files` page, click "Download" next to the desired file

3. Delete a processed file:
   - On the `/files` page, click "Delete" next to the file you want to remove

## Troubleshooting

If you encounter any issues:

1. Check the application logs for error messages.
2. Ensure all dependencies are correctly installed.
3. Verify that Redis is running and accessible.
4. Make sure the input files are in supported formats and not corrupted.
5. Check that the output directory is writable.

If problems persist, please check the GitHub Issues page or create a new issue with details about the problem you're experiencing.

## Contributing

We welcome contributions to DocuRefine! Please see our CONTRIBUTING.md file for more information on how to get started.

## License

DocuRefine is released under the MIT License. See the LICENSE file for more details.