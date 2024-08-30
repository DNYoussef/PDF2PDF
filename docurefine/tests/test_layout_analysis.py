import unittest
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from src.layout_analysis import analyze_layout, merge_ocr_and_layout

class TestLayoutAnalysis(unittest.TestCase):
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
        d.text((10,10), "Title", fill='black', font=font)
        d.text((10,50), "Content", fill='black', font=font)
        img.save(path)

    def test_analyze_layout(self):
        result = analyze_layout(self.sample_image_path)
        self.assertTrue(len(result) > 0)
        self.assertIn('type', result[0])
        self.assertIn('coordinates', result[0])
        self.assertIn('score', result[0])

    def test_merge_ocr_and_layout(self):
        ocr_result = {
            'text': 'Title Content',
            'layout': [
                {'text': 'Title', 'left': 10, 'top': 10, 'width': 50, 'height': 20},
                {'text': 'Content', 'left': 10, 'top': 50, 'width': 70, 'height': 20}
            ]
        }
        layout_elements = [
            {'type': 'Title', 'coordinates': (5, 5, 60, 35), 'score': 0.9},
            {'type': 'Text', 'coordinates': (5, 45, 80, 75), 'score': 0.8}
        ]
        result = merge_ocr_and_layout(ocr_result, layout_elements)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'Title')
        self.assertEqual(result[0]['text'], 'Title')
        self.assertEqual(result[1]['type'], 'Text')
        self.assertEqual(result[1]['text'], 'Content')

if __name__ == '__main__':
    unittest.main()