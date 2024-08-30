import unittest
import os
import tempfile
from src.pdf_utils import split_document, split_pdf, reconstruct_pdf
from PyPDF2 import PdfReader

class TestPdfUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_pdf_path = os.path.join(self.test_dir, "sample.pdf")
        self.create_sample_pdf(self.sample_pdf_path)

    def tearDown(self):
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def create_sample_pdf(self, path):
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(path)
        c.drawString(100, 100, "Page 1")
        c.showPage()
        c.drawString(100, 100, "Page 2")
        c.showPage()
        c.save()

    def test_split_document_pdf(self):
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        result = split_document(self.sample_pdf_path, output_dir)
        self.assertEqual(len(result), 2)
        for path in result:
            self.assertTrue(os.path.exists(path))

    def test_split_pdf(self):
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        result = split_pdf(self.sample_pdf_path, output_dir)
        self.assertEqual(len(result), 2)
        for path in result:
            self.assertTrue(os.path.exists(path))

    def test_reconstruct_pdf(self):
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        split_pages = split_pdf(self.sample_pdf_path, output_dir)
        
        processed_pages = [{'refined_image_path': path} for path in split_pages]
        output_path = os.path.join(self.test_dir, "reconstructed.pdf")
        reconstruct_pdf(processed_pages, output_path)
        
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'rb') as f:
            pdf = PdfReader(f)
            self.assertEqual(len(pdf.pages), 2)

if __name__ == '__main__':
    unittest.main()