import unittest
from unittest.mock import patch, MagicMock
from src.celery_tasks import process_document

class TestCeleryTasks(unittest.TestCase):
    @patch('src.celery_tasks.split_pdf')
    @patch('src.celery_tasks.process_page')
    @patch('src.celery_tasks.reconstruct_pdf')
    def test_process_document(self, mock_reconstruct_pdf, mock_process_page, mock_split_pdf):
        # Set up mock return values
        mock_split_pdf.return_value = ["page1.png", "page2.png"]
        mock_process_page.return_value = MagicMock()
        mock_reconstruct_pdf.return_value = {"output_pdf_path": "output.pdf"}

        # Call the function
        result = process_document("input.pdf", "output_dir")

        # Assert the result
        self.assertIsNotNone(result)
        self.assertEqual(mock_split_pdf.call_count, 1)
        self.assertEqual(mock_process_page.call_count, 2)  # Called for each page
        self.assertEqual(mock_reconstruct_pdf.call_count, 1)

if __name__ == '__main__':
    unittest.main()