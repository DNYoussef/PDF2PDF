import cv2
from skimage.metrics import structural_similarity as ssim
from config.config import config
import numpy as np

def compare_images(image1_path, image2_path):
    """
    Compare two images using Structural Similarity Index (SSIM).
    
    :param image1_path: Path to the first image
    :param image2_path: Path to the second image
    :return: SSIM score (float between -1 and 1, where 1 means perfect similarity)
    """
    # Read images
    img1 = cv2.imread(image1_path)
    img2 = cv2.imread(image2_path)
    
    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Compute SSIM between the two images
    score, diff = ssim(gray1, gray2, full=True)
    
    return score, diff

def refine_image(original_image_path, refined_image_path, threshold=0.95):
    """
    Compare the original and refined images, and perform additional refinement if needed.
    
    :param original_image_path: Path to the original image
    :param refined_image_path: Path to the refined image
    :param threshold: SSIM threshold for accepting the refined image
    :return: Path to the final refined image
    """
    similarity_score, diff = compare_images(original_image_path, refined_image_path)
    
    if similarity_score >= threshold:
        return refined_image_path
    
    # If similarity is below threshold, perform additional refinement
    original_img = cv2.imread(original_image_path)
    refined_img = cv2.imread(refined_image_path)
    
    # Convert the difference map to uint8 and apply threshold
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mask for the areas that need refinement
    mask = np.zeros(original_img.shape[:2], dtype="uint8")
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Ignore small contours
            cv2.drawContours(mask, [contour], 0, 255, -1)
    
    # Apply the mask to the original image
    result = cv2.bitwise_and(original_img, original_img, mask=mask)
    result = cv2.add(refined_img, result)
    
    # Save the result
    final_refined_path = refined_image_path.replace('.png', '_final.png')
    cv2.imwrite(final_refined_path, result)
    
    return final_refined_path

# Additional image comparison functions can be added here