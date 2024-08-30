import unittest
import os
import tempfile
import numpy as np
from src.latex_converter import text_to_latex, convert_layout_to_latex, render_latex, latex_to_image

class TestLatexConverter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def test_text_to_latex(self):
        input_text = "x squared plus y squared equals z squared"
        result = text_to_latex(input_text)
        self.assertIn("x^2", result)
        self.assertIn("y^2", result)
        self.assertIn("z^2", result)

    def test_convert_layout_to_latex(self):
        merged_layout = [
            {'type': 'Title', 'text': 'Sample Document'},
            {'type': 'Text', 'text': 'This is a paragraph.'},
            {'type': 'List', 'text': 'Item 1\nItem 2'},
            {'type': 'Figure', 'text': 'Figure 1'}
        ]
        result = convert_layout_to_latex(merged_layout)
        self.assertIn("\\section{Sample Document}", result)
        self.assertIn("This is a paragraph", result)
        self.assertIn("\\begin{itemize}", result)
        self.assertIn("\\item", result)
        self.assertIn("\\begin{figure}", result)

    def test_render_latex(self):
        latex_content = "$x^2 + y^2 = z^2$"
        output_path = os.path.join(self.test_dir, "output.png")
        render_latex(latex_content, output_path)
        self.assertTrue(os.path.exists(output_path))

    def test_latex_to_image(self):
        latex_content = "$x^2 + y^2 = z^2$"
        result = latex_to_image(latex_content)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result.shape), 3)  # Should be a 3D array (height, width, channels)

if __name__ == '__main__':
    unittest.main()