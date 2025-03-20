# tests/test_agent.py
import unittest
import numpy as np
from src.agent import agent
from src.environment import terrain, resource # Import needed

class TestAgent(unittest.TestCase):

    def setUp(self):
        # Create a sample terrain and resource map for testing
        self.width = 10
        self.height = 10
        self.terrain = terrain.generate_heightmap(self.width, self.height)
        self.resource_map, _ = resource.distribute_resources(self.terrain, 3)
        self.agent = agent.Agent(x=5, y=5) #Call the agent here.

    def test_move(self):
        initial_x = self.agent.x
        initial_y = self.agent.y
        initial_energy = self.agent.energy

        # Try a valid move
        moved = self.agent.move(1, 0, self.terrain, 0.1) #Added the delta parameter here.
        self.assertTrue(moved) #Agent has moved.
        self.assertEqual(self.agent.x, initial_x + 1) #Position should be X+1.
        self.assertLess(self.agent.energy, initial_energy)  # Energy should have decreased

        # Try an invalid move (out of bounds)
        self.agent.x = 0 #Reset the location to 0
        self.agent.y = 0
        moved = self.agent.move(-1, 0, self.terrain, 0.1)
        self.assertFalse(moved) #Should return that the agent could not move.
        self.assertEqual(self.agent.x, 0)

    def test_collect_resource(self):
        #Place a resource next to the agent.
        self.resource_map[self.agent.y][self.agent.x + 1] = 1
        #Initial variables.
        initial_energy = self.agent.energy
        initial_resource = self.agent.collected_resources
        #Call the collect action.
        self.agent.collect_resource(self.resource_map, self.agent.x + 1, self.agent.y)

        #Assert that the values changed.
        self.assertGreater(self.agent.energy, initial_energy)
        self.assertGreater(self.agent.collected_resources, initial_resource)

    def test_update(self):
        #Test the update function.
        initial_x = self.agent.x
        initial_y = self.agent.y
        initial_energy = self.agent.energy
        #Force it to move.
        self.resource_map[self.agent.y][self.agent.x+1] = 1
        # Try a valid move
        self.agent.update(self.terrain, self.resource_map, 0.1) #Added the delta parameter.
        self.assertNotEqual(self.agent.x, initial_x) #They should be different.
        self.assertNotEqual(self.agent.y, initial_y)
        self.assertLess(self.agent.energy, initial_energy)

    def test_is_alive(self):
        self.assertTrue(self.agent.is_alive()) #Should return true, because the health is above 0.
        self.agent.energy = 0 #Set the agent's health to 0.
        self.assertFalse(self.agent.is_alive()) #Should return false, because the health is 0.

    # tests/test_agent.py
# ... (rest of the code) ...
    def test_find_nearest_resource(self):
        #Test the agent find the nearest resource.
        #Set up the resources
        self.resource_map[2][2] = 1 #Make there a resource here.
        nearest_resource = self.agent.find_nearest_resource(self.resource_map)
        #Convert the NumPy integers to regular Python integers for comparison
        if nearest_resource:
            nearest_resource = (int(nearest_resource[0]), int(nearest_resource[1]))

        self.assertEqual(nearest_resource, (2,2)) #Check to see if it returns the correct cords.

if __name__ == '__main__':
    unittest.main()