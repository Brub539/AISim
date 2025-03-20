# tests/test_terrain.py
import unittest
import numpy as np
from src.environment import terrain

class TestTerrain(unittest.TestCase):

    def test_generate_heightmap(self):
        width = 10
        height = 10
        heightmap = terrain.generate_heightmap(width, height)
        self.assertEqual(heightmap.shape, (height, width))
        self.assertIsInstance(heightmap, np.ndarray)

    def test_get_height(self):
        width = 10
        height = 10
        heightmap = np.zeros((height, width))
        heightmap[5, 5] = 1.0
        self.assertEqual(terrain.get_height(heightmap, 5, 5), 1.0)
        self.assertEqual(terrain.get_height(heightmap, 0, 0), 0.0)
        self.assertEqual(terrain.get_height(heightmap, -1, -1), 0.0)  # Out of bounds

    def test_is_walkable(self):
        width = 10
        height = 10
        heightmap = np.zeros((height, width))
        self.assertTrue(terrain.is_walkable(heightmap, 5, 5))  # Flat terrain is walkable
        # Add a steep slope (example - adjust values as needed)
        heightmap[6, 5] = 2.0
        self.assertFalse(terrain.is_walkable(heightmap, 5, 5)) #Should return false, because the terrain is no longer walkable.
        #print("Slope: ", terrain.calculate_slope(heightmap, 5, 5)) #For debugging purposes.

    def test_calculate_slope(self):
        width = 10
        height = 10
        heightmap = np.zeros((height, width))
        heightmap[5, 5] = 1.0
        heightmap[6, 5] = 2.0
        slope = terrain.calculate_slope(heightmap, 5, 5)
        self.assertGreaterEqual(slope, 0)  # Slope should be non-negative

if __name__ == '__main__':
    unittest.main()