# src/integration_test.py
import numpy as np
from environment import terrain, resource
from agent import agent

def main():
    width = 30
    height = 20
    num_resources = 15
    num_agents = 3
    time_steps = 10

    # Initialize Environment
    _terrain = terrain.generate_heightmap(width, height)
    resource_map, resource_locations = resource.distribute_resources(_terrain, num_resources)

    # Initialize Agents
    agents = []
    for _ in range(num_agents):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        agents.append(agent.Agent(x=x, y=y))

    # Simulation Loop
    for time_step in range(time_steps):
        # Update Agents and Environment
        for ag in agents:
            resource_map = ag.update(_terrain, resource_map, 0.1)  # Update agent and resource map
        #Print for debbug purposes, this ensure the code is being run.
        print(f"Time step: ", time_step)

    print("Integration test completed without errors.")

if __name__ == "__main__":
    main()