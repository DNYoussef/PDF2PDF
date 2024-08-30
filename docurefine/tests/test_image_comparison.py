import unittest
import os
import tempfile
import cv2
import numpy as np
from src.image_comparison import compare_images, refine_image

class TestImageComparison(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
        # Create test images
        self.image1_path = os.path.join(self.test_dir, "image1.png")
        self.image2_path = os.path.join(self.test_dir, "image2.png")
        
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img2[40:60, 40:60] = 0  # Add a black square to make images different
        
        cv2.imwrite(self.image1_path, img1)
        cv2.imwrite(self.image2_path, img2)
    
    def tearDown(self):
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_compare_images(self):
        score, diff = compare_images(self.image1_path, self.image2_path)
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
        self.assertLess(score, 1)
        self.assertIsInstance(diff, np.ndarray)
    
    def test_refine_image(self):
        refined_path = refine_image(self.image1_path, self.image2_path, threshold=0.9)
        self.assertTrue(os.path.exists(refined_path))
        self.assertNotEqual(refined_path, self.image2_path)
        
        # Test with identical images
        identical_refined_path = refine_image(self.image1_path, self.image1_path, threshold=0.9)
        self.assertEqual(identical_refined_path, self.image1_path)

if __name__ == '__main__':
    unittest.main()