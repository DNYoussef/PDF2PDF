import logging
import os
from celery import Celery, group
from celery.exceptions import MaxRetriesExceededError
from pdf_utils import split_pdf, reconstruct_pdf
from ocr import perform_ocr_with_layout, perform_ocr
from layout_analysis import analyze_layout, merge_ocr_and_layout
from latex_converter import convert_layout_to_latex
from image_comparison import refine_image
from config.config import config
import cv2
import numpy as np
from functools import lru_cache
import matplotlib.pyplot as plt
import io
from PIL import Image
from celery import chord
from multiprocessing import Pool
import PyPDF2
from .profiling import profile_function

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery('docurefine', broker=config.CELERY_BROKER_URL, backend=config.CELERY_RESULT_BACKEND)

@lru_cache(maxsize=100)
def cached_perform_ocr(image_path):
    return perform_ocr(image_path)

@lru_cache(maxsize=100)
def cached_analyze_layout(image_path):
    return analyze_layout(image_path)

def process_chunk(chunk_data):
    chunk, latex_content = chunk_data
    refined_chunk = refine_image_with_latex(chunk, latex_content)
    return refined_chunk

@app.task(bind=True, max_retries=3)
def process_page(self, page_path, output_directory):
    try:
        logger.info(f"Processing page: {page_path}")
        
        # Perform OCR with layout
        ocr_result = perform_ocr_with_layout(page_path)
        
        # Analyze layout
        layout_elements = analyze_layout(page_path)
        
        # Merge OCR and layout results
        merged_layout = merge_ocr_and_layout(ocr_result, layout_elements)
        
        # Convert to LaTeX
        latex_content = convert_layout_to_latex(merged_layout)
        
        # Generate a refined image based on LaTeX content
        refined_image_path = os.path.join(output_directory, f"refined_{os.path.basename(page_path)}")
        generate_image_from_latex(latex_content, refined_image_path)
        
        # Further refine the image if necessary
        final_refined_path = refine_image(page_path, refined_image_path)
        
        logger.info(f"Successfully processed page: {page_path}")
        return {
            'page_path': page_path,
            'latex_content': latex_content,
            'refined_image_path': final_refined_path
        }
    except Exception as e:
        logger.error(f"Error processing page {page_path}: {str(e)}")
        try:
            self.retry(countdown=60)  # Retry after 1 minute
        except MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for page {page_path}")
            raise

def split_image(image, num_chunks):
    height, width = image.shape[:2]
    chunk_height = height // num_chunks
    return [image[i:i+chunk_height] for i in range(0, height, chunk_height)]

def merge_chunks(chunks):
    return np.vstack(chunks)

@app.task(bind=True, max_retries=3)
def process_document(self, input_path, output_directory):
    try:
        logger.info(f"Starting document processing: {input_path}")
        
        # Split PDF (if input is PDF)
        if input_path.lower().endswith('.pdf'):
            page_paths = split_pdf(input_path, output_directory)
        else:
            page_paths = [input_path]  # Single image input
        
        # Process pages in parallel using a chord
        header = [process_page.s(page_path, output_directory) for page_path in page_paths]
        callback = reconstruct_pdf.s(output_directory)
        result = chord(header)(callback)
        
        logger.info(f"Document processing complete. Results saved in {output_directory}")
        return result.get()
    except Exception as e:
        logger.error(f"Error processing document {input_path}: {str(e)}")
        try:
            self.retry(countdown=300)  # Retry after 5 minutes
        except MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for document {input_path}")
            raise

@app.task
def reconstruct_pdf(processed_pages, output_directory):
    output_pdf_path = os.path.join(output_directory, "reconstructed.pdf")
    # ... (existing reconstruct_pdf logic)
    return {'output_pdf_path': output_pdf_path}

def refine_image_with_latex(image, latex_content, layout_elements):
    """
    Refine the image using LaTeX content and layout information.
    
    :param image: Original image as a numpy array
    :param latex_content: LaTeX content extracted from the image
    :param layout_elements: Layout information extracted from the image
    :return: Refined image as a numpy array
    """
    # Create a copy of the original image
    refined_image = image.copy()
    
    # Iterate through layout elements and apply refinements
    for element in layout_elements:
        if element['type'] == 'text':
            # Replace text areas with rendered LaTeX
            x, y, w, h = element['coordinates']
            latex_snippet = latex_content[element['text_index']]
            rendered_text = render_latex(latex_snippet, (w, h))
            refined_image[y:y+h, x:x+w] = rendered_text
        elif element['type'] == 'figure':
            # Enhance figure areas (e.g., increase contrast, remove noise)
            x, y, w, h = element['coordinates']
            figure_area = refined_image[y:y+h, x:x+w]
            enhanced_figure = enhance_figure(figure_area)
            refined_image[y:y+h, x:x+w] = enhanced_figure
    
    return refined_image

def render_latex(latex_snippet, size):
    """
    Render LaTeX snippet to an image using matplotlib.
    
    :param latex_snippet: LaTeX content to render
    :param size: Size of the output image (width, height)
    :return: Rendered LaTeX as a numpy array
    """
    fig = plt.figure(figsize=(size[0]/100, size[1]/100), dpi=100)
    plt.text(0.5, 0.5, f'${latex_snippet}$', size=12, ha='center', va='center')
    plt.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    buf.seek(0)
    img = Image.open(buf)
    return np.array(img)

def enhance_figure(figure):
    """
    Enhance a figure by increasing contrast and removing noise.
    
    :param figure: Input figure as a numpy array
    :return: Enhanced figure as a numpy array
    """
    # Increase contrast
    enhanced = cv2.convertScaleAbs(figure, alpha=1.5, beta=0)
    
    # Remove noise using a median filter
    enhanced = cv2.medianBlur(enhanced, 3)
    
    return enhanced

def generate_image_from_latex(latex_content, output_path):
    """
    Generate an image from LaTeX content.
    
    :param latex_content: LaTeX content to render
    :param output_path: Path to save the generated image
    """
    fig = plt.figure(figsize=(8.5, 11))  # Standard letter size
    plt.axis('off')
    plt.text(0.5, 0.5, f'${latex_content}$', size=12, ha='center', va='center', wrap=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

@app.task(bind=True, max_retries=3)
def process_multiple_documents(self, file_list):
    try:
        logger.info(f"Starting processing of multiple documents: {len(file_list)} files")
        
        results = []
        for input_path, output_directory in file_list:
            result = process_document(input_path, output_directory)
            results.append(result)
        
        # Merge all processed PDFs into a single file
        merged_pdf_path = merge_pdfs([result['output_pdf_path'] for result in results])
        
        logger.info(f"All documents processed. Results saved in respective output directories.")
        return results + [{'output_pdf_path': merged_pdf_path}]
    except Exception as e:
        logger.error(f"Error processing multiple documents: {str(e)}")
        try:
            self.retry(countdown=300)  # Retry after 5 minutes
        except MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for processing multiple documents")
            raise

def merge_pdfs(pdf_paths):
    merged_pdf = PyPDF2.PdfMerger()
    for pdf_path in pdf_paths:
        merged_pdf.append(pdf_path)
    
    merged_pdf_path = os.path.join(os.path.dirname(pdf_paths[0]), "merged_output.pdf")
    merged_pdf.write(merged_pdf_path)
    merged_pdf.close()
    
    return merged_pdf_path