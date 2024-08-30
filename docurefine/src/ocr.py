import pytesseract
from PIL import Image

def perform_ocr(image_path):
    """
    Perform OCR on the given image.
    
    :param image_path: Path to the input image
    :return: Extracted text as a string
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def perform_ocr_with_layout(image_path):
    """
    Perform OCR on the given image and return layout information.
    
    :param image_path: Path to the input image
    :return: Dictionary containing extracted text and layout information
    """
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    result = {
        'text': ' '.join(data['text']),
        'layout': []
    }
    
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Only consider text with confidence > 60%
            result['layout'].append({
                'text': data['text'][i],
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            })
    
    return result

# Additional OCR-related functions can be added here