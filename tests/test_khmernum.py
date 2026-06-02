"""
Unit tests for KhmerNum application
"""
import unittest
from khmernum.app import KhmerNumApp


class TestKhmerNumApp(unittest.TestCase):
    """Test cases for KhmerNumApp"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = KhmerNumApp(rows=10, cols=10)
    
    def test_initialization(self):
        """Test app initialization"""
        self.assertEqual(self.app.rows, 10)
        self.assertEqual(self.app.cols, 10)
        self.assertEqual(len(self.app.pixels), 10)
        self.assertEqual(len(self.app.pixels[0]), 10)
    
    def test_all_pixels_off_initially(self):
        """Test that all pixels are off at initialization"""
        for row in self.app.pixels:
            for pixel in row:
                self.assertFalse(pixel)
    
    def test_get_clicked_box(self):
        """Test click detection"""
        # Click on first box (top-left)
        result = self.app.get_clicked_box((10, 50))
        self.assertIsNotNone(result)
        self.assertEqual(result, (0, 0))
        
        # Click outside grid
        result = self.app.get_clicked_box((1000, 1000))
        self.assertIsNone(result)
    
    def test_clear_panel(self):
        """Test panel clearing"""
        # Set some pixels to ON
        self.app.pixels[0][0] = True
        self.app.pixels[1][1] = True
        
        # Clear panel
        self.app.clear_panel()
        
        # Check all pixels are OFF
        for row in self.app.pixels:
            for pixel in row:
                self.assertFalse(pixel)


if __name__ == "__main__":
    unittest.main()
