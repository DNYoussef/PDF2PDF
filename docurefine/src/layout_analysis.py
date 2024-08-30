import layoutparser as lp
import cv2

def analyze_layout(image_path):
    """
    Analyze the layout of a given image using LayoutParser.
    
    :param image_path: Path to the input image
    :return: List of detected layout elements
    """
    # Load the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Load a pre-trained model
    model = lp.models.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config')

    # Detect layout elements
    layout = model.detect(image)

    # Process and return the detected elements
    elements = []
    for element in layout:
        elements.append({
            'type': element.type,
            'coordinates': element.coordinates,
            'score': element.score
        })

    return elements

def merge_ocr_and_layout(ocr_result, layout_elements):
    """
    Merge OCR results with layout analysis.
    
    :param ocr_result: Result from OCR with layout information
    :param layout_elements: Result from layout analysis
    :return: Merged layout information
    """
    merged_layout = []
    
    for layout_element in layout_elements:
        matching_text = []
        for ocr_element in ocr_result['layout']:
            if rectangles_overlap(layout_element['coordinates'], ocr_element):
                matching_text.append(ocr_element['text'])
        
        merged_layout.append({
            'type': layout_element['type'],
            'coordinates': layout_element['coordinates'],
            'text': ' '.join(matching_text)
        })
    
    return merged_layout

def rectangles_overlap(rect1, rect2):
    """
    Check if two rectangles overlap.
    
    :param rect1: First rectangle (x1, y1, x2, y2)
    :param rect2: Second rectangle (left, top, width, height)
    :return: Boolean indicating if rectangles overlap
    """
    x1, y1, x2, y2 = rect1
    left, top, width, height = rect2['left'], rect2['top'], rect2['width'], rect2['height']
    
    return not (x2 < left or x1 > left + width or y2 < top or y1 > top + height)

# Additional layout analysis functions can be added here