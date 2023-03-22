import unittest
from PIL import Image
import numpy as np 

from pixelpictures.image_to_pixels import distance_colors, get_color, resize, to_pixels

# Unit testing image_to_pixels functions
class ImageToPixelsTestCase(unittest.TestCase):

    def setUp(self):
        self.image = Image.open('pixelpictures/tests/manda.jpg')

    def test_distance_colors(self):
        color1 = (123,200,22)
        color2 = (124,200,22)
        white = (255,255,255)
        black = (0,0,0)
        gray = (123,123,123)
        self.assertEqual(distance_colors(color1, color1), 0)
        self.assertNotEqual(distance_colors(color1, color2), 0)
        self.assertTrue(distance_colors(white,black) > distance_colors(white,gray))

    def test_get_color(self):
        prev_color = (125,125,125)
        colors_with_prev_color = [(0,0,0), (100,230,100), (125,125,125), (255,255,255)]
        colors_without_prev_color = [(0,0,0), (100,230,100), (255,255,255)]
        self.assertTrue(get_color(prev_color, colors_with_prev_color) == (125,125,125))
        self.assertTrue(get_color(prev_color, colors_without_prev_color) != (125,125,125))

    def test_resize(self):
        resized = resize(15, 10, self.image)
        self.assertEqual(resized.width, 15)
        self.assertEqual(resized.height, 10)

    def test_to_pixels(self):
        resized = resize(20, 30, self.image)
        resized_arr = np.array(resized)
        colors = [(0,0,0), (255,255,255), (155,155,155)]
        pixel_image = to_pixels(resized_arr, colors)

        #Check which colors are in pixel_image: 
        all_in_colors = True
        for i in range(30):
            for j in range(20):
                if not pixel_image[i][j] in colors:
                    self.fail(f'Color {pixel_image[i][j]} not in colors.')
        
        # Check sizes:
        self.assertEqual(len(pixel_image), 30)
        self.assertEqual(len(pixel_image[0]), 20)