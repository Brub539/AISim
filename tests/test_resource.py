# tests/test_resource.py
import unittest
import numpy as np
from src.environment import resource, terrain

class TestResource(unittest.TestCase):

    def setUp(self):
        # Create a sample terrain for testing
        self.width = 10
        self.height = 10
        self.terrain = terrain.generate_heightmap(self.width, self.height) #Have to import the terrain generator.

    def test_distribute_resources(self):
        num_resources = 5
        resource_map, resource_locations = resource.distribute_resources(self.terrain, num_resources)
        self.assertEqual(len(resource_locations), num_resources)
        self.assertEqual(resource_map.sum(), num_resources) #The number of resources should equal the sum.

    def test_deplete_resource(self):
        resource_map = np.zeros((self.height, self.width))
        resource_map[5, 5] = 1.0
        resource_map = resource.deplete_resource(resource_map, 5, 5)
        self.assertEqual(resource_map[5, 5], 0.0) #The resource should be zero.

    def test_regenerate_resource(self):
        resource_map = np.zeros((self.height, self.width))
        resource_map[5, 5] = 0.0
        resource_map = resource.regenerate_resource(resource_map, self.terrain, 5, 5)
        self.assertGreater(resource_map[5, 5], 0.0)  # Resource should be greater than 0 after regeneration

    def test_get_resource_amount(self):
        resource_map = np.zeros((self.height, self.width))
        resource_map[5, 5] = 0.5
        self.assertEqual(resource.get_resource_amount(resource_map, 5, 5), 0.5)

if __name__ == '__main__':
    unittest.main()