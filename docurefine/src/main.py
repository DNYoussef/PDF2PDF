import argparse
import os
from celery_tasks import process_document

def main():
    parser = argparse.ArgumentParser(description="DocuRefine: Transform poorly formatted documents into searchable, editable PDFs.")
    parser.add_argument("input_path", help="Path to the input document (PDF or image)")
    parser.add_argument("output_directory", help="Directory to save the processed results")
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print(f"Error: Input file '{args.input_path}' does not exist.")
        return

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    print(f"Processing document: {args.input_path}")
    print(f"Output directory: {args.output_directory}")

    # Start the document processing
    process_document.delay(args.input_path, args.output_directory)
    print("Document processing started. Check Celery worker logs for progress.")

if __name__ == "__main__":
    main()