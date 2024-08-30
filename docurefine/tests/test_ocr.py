import unittest
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from src.ocr import perform_ocr, perform_ocr_with_layout

class TestOCR(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_image_path = os.path.join(self.test_dir, "sample.png")
        self.create_sample_image(self.sample_image_path)

    def tearDown(self):
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def create_sample_image(self, path):
        img = Image.new('RGB', (300, 100), color='white')
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        d.text((10,10), "Hello, World!", fill='black', font=font)
        img.save(path)

    def test_perform_ocr(self):
        result = perform_ocr(self.sample_image_path)
        self.assertIn("Hello, World!", result)

    def test_perform_ocr_with_layout(self):
        result = perform_ocr_with_layout(self.sample_image_path)
        self.assertIn("text", result)
        self.assertIn("layout", result)
        self.assertIn("Hello, World!", result['text'])
        self.assertTrue(len(result['layout']) > 0)

if __name__ == '__main__':
    unittest.main()