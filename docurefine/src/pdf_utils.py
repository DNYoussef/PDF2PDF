import PyPDF2
import os
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import docx2pdf
import io
import pdfkit

def split_document(input_path, output_directory):
    """
    Split a document into individual pages.
    
    :param input_path: Path to the input document
    :param output_directory: Directory to save individual pages
    :return: List of paths to individual page images
    """
    file_extension = os.path.splitext(input_path)[1].lower()
    
    if file_extension == '.pdf':
        return split_pdf(input_path, output_directory)
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        return [input_path]
    elif file_extension == '.docx':
        return split_docx(input_path, output_directory)
    elif file_extension == '.html':
        return split_html(input_path, output_directory)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def split_pdf(input_path, output_directory):
    """
    Split a PDF file into individual pages.
    
    :param input_path: Path to the input PDF file
    :param output_directory: Directory to save individual pages
    :return: List of paths to individual page PDFs
    """
    with open(input_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        output_paths = []
        
        for page_num in range(len(pdf.pages)):
            output = PyPDF2.PdfWriter()
            output.add_page(pdf.pages[page_num])
            
            output_path = f"{output_directory}/page_{page_num + 1}.pdf"
            with open(output_path, 'wb') as output_file:
                output.write(output_file)
            
            output_paths.append(output_path)
    
    return output_paths

def split_docx(input_path, output_directory):
    # Convert DOCX to PDF
    pdf_path = os.path.join(output_directory, 'temp.pdf')
    docx2pdf.convert(input_path, pdf_path)
    
    # Split the PDF
    pages = split_pdf(pdf_path, output_directory)
    
    # Remove the temporary PDF
    os.remove(pdf_path)
    
    return pages

def split_html(input_path, output_directory):
    # Convert HTML to PDF
    pdf_path = os.path.join(output_directory, 'temp.pdf')
    
    # Use pdfkit to convert HTML to PDF
    import pdfkit
    pdfkit.from_file(input_path, pdf_path)
    
    # Split the PDF
    pages = split_pdf(pdf_path, output_directory)
    
    # Remove the temporary PDF
    os.remove(pdf_path)
    
    return pages

def reconstruct_pdf(processed_pages, output_path):
    """
    Reconstruct the final PDF from processed pages.
    
    :param processed_pages: List of dictionaries containing processed page data
    :param output_path: Path to save the reconstructed PDF
    """
    pdf_writer = PdfWriter()

    for page_data in processed_pages:
        refined_image_path = page_data['refined_image_path']
        pdf_page = convert_image_to_pdf_page(refined_image_path)
        pdf_writer.add_page(pdf_page)

    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)

    print(f"Reconstructed PDF saved to: {output_path}")

def convert_image_to_pdf_page(image_path):
    """
    Convert an image to a PDF page.
    
    :param image_path: Path to the image file
    :return: A PDF page object
    """
    image = Image.open(image_path)
    pdf_bytes = io.BytesIO()
    image.save(pdf_bytes, format='PDF')
    pdf_bytes.seek(0)
    return PdfReader(pdf_bytes).pages[0]

# Additional PDF utility functions can be added here