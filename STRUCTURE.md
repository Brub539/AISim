# Project Structure: Evolving AI Agents

This document outlines the directory structure for the "Evolving AI Agents" project.

## Root Directory (`EvolvingAIAgents/`)
EvolvingAIAgents/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── data/
├── docs/
├── src/
├── tests/
└── config/
├──main.py

## `src/` Directory Structure
src/
├── __init__.py       (Makes the src directory a Python package)
├── environment/      (Code related to the simulation environment)
│   ├── __init__.py   (Makes the environment directory a Python package)
│   ├── terrain.py    (Terrain generation and management)
│   │   ├── `generate_heightmap(width, height)`: Generates a 2D heightmap representing the terrain.  Could use Perlin noise, Simplex noise, or other procedural generation techniques.
│   │   ├── `get_height(x, y)`: Returns the height of the terrain at a given (x, y) coordinate.
│   │   ├── `is_walkable(x, y)`: Checks if a given (x, y) coordinate is walkable (not too steep, not water, etc.).
│   │   └── `calculate_slope(x, y)`: Calculates the slope of the terrain at a given (x, y) coordinate.
│   ├── resource.py   (Resource distribution and management)
│   │   ├── `distribute_resources(terrain, num_resources, resource_type)`: Distributes resources randomly on the terrain, potentially influenced by terrain features.
│   │   ├── `deplete_resource(x, y, amount)`: Depletes a resource at a given (x, y) coordinate.
│   │   ├── `regenerate_resource(x, y, rate)`: Regenerates a resource at a given (x, y) coordinate, influenced by sunlight and other factors.
│   │   └── `get_resource_amount(x, y)`: Returns the amount of resource at a given (x, y) coordinate.
│   ├── sunlight.py   (Sunlight simulation logic)
│   │   ├── `calculate_sunlight_intensity(time)`: Calculates sunlight intensity based on the time of day (e.g., using a sine wave).
│   │   ├── `get_sunlight_angle(time)`: Returns the angle of the sunlight based on the time of day. This could be used for shading effects.
│   │   └── `apply_shadow(terrain, sunlight_angle)`: (Optional) Applies shadowing effects to the terrain based on the sunlight angle.
│   └── environment_manager.py (Overall management of the environment)
│       ├── `__init__(terrain, resource_manager, sunlight)`: Initializes the environment manager with instances of terrain, resource manager, and sunlight.
│       ├── `update_environment(time)`: Updates the environment based on the current time (e.g., regenerates resources, calculates sunlight intensity).
│       ├── `get_environment_state()`: Returns the current state of the environment (e.g., terrain heightmap, resource distribution, sunlight intensity).
│       └── `is_within_bounds(x, y)`: Checks if a given (x, y) coordinate is within the bounds of the environment.
├── agent/            (Code related to the AI agent)
│   ├── __init__.py   (Makes the agent directory a Python package)
│   ├── agent.py       (Main agent class)
│   │   ├── `__init__(genome, x, y)`: Initializes an agent with a given genome, starting position, and initial energy.
│   │   ├── `move(direction, terrain)`: Moves the agent in a given direction, consuming energy based on the terrain and the agent's `hacns1` gene.
│   │   ├── `collect_resource(resource)`: Collects a resource, gaining energy based on the resource type and the agent's `dietary_flexibility` gene.
│   │   ├── `update()`: Updates the agent's state (e.g., checks if it's dead, regenerates energy, performs actions).
│   │   ├── `is_alive()`: Returns True if the agent's energy is above zero, False otherwise.
│   │   ├── `get_position()`: Returns the agent's current (x, y) coordinates.
│   │   └── `get_energy()`: Returns the agent's current energy level.
│   ├── genome.py      (Agent's genetic code)
│   │   ├── `__init__(initial_genes=None)`: Initializes a genome with a set of genes.  If `initial_genes` is None, genes are initialized randomly.
│   │   ├── `get_gene(gene_name)`: Returns the value of a given gene.
│   │   ├── `mutate(mutation_rate)`: Mutates the genome, randomly changing gene values with a given probability.
│   │   ├── `crossover(other_genome)`: Performs crossover with another genome, creating a new genome with a combination of genes from both parents.
│   │   └── `get_all_genes()`: Returns a dictionary of all gene names and their values.
│   ├── vision.py      (Raycasting and vision processing)
│   │   ├── `raycast(terrain, agent_x, agent_y, angle, max_distance)`: Performs a raycast in a given direction, returning the distance to the nearest object (resource, terrain) and its type.
│   │   ├── `process_vision(terrain, agent_x, agent_y)`: Uses raycasting to create a vision array representing the agent's surroundings.
│   │   └── `get_visible_resources(resource_map, agent_x, agent_y)`: Returns a list of visible resources within the agent's field of view.
│   ├── movement.py    (Movement logic and energy consumption)
│   │   ├── `calculate_energy_cost(terrain, distance, hacns1)`: Calculates the energy cost of moving a given distance on a given terrain, influenced by the `hacns1` gene.
│   │   ├── `apply_bipedalism_bonus(bipedalism_gene, terrain_type)`: Applies a bonus to movement speed or energy consumption based on the `bipedalism` gene and the terrain type.
│   │   └── `move_agent(agent, direction, terrain)`: Moves the agent in a given direction, consuming energy and updating its position.
│   ├── social.py      (Social interaction logic)
│   │   ├── `calculate_social_affinity(agent1, agent2, social_bonding_gene)`: Calculates the social affinity between two agents based on their `social_bonding` gene.
│   │   ├── `move_towards_group(agent, other_agents)`: Moves the agent towards a group of other agents with high social affinity.
│   │   └── `communicate(agent1, agent2)`: Simulates communication between agents, potentially increasing the efficiency of cooperation if `hacns1` is high.
│   └── ai_controller.py (RNN or other AI controller)
│       ├── `__init__(input_size, hidden_size, output_size)`: Initializes the AI controller with given input, hidden, and output sizes.
│       ├── `forward(vision_data)`: Processes vision data through the neural network and returns movement commands.
│       └── `train(vision_data, reward)`: Trains the neural network based on vision data and a reward signal.
├── genetic_algorithm/ (Code related to the genetic algorithm)
│   ├── __init__.py   (Makes the genetic_algorithm directory a Python package)
│   ├── genetic_algorithm.py  (Implementation of the GA)
│   │   ├── `__init__(population_size, mutation_rate)`: Initializes the genetic algorithm with a given population size and mutation rate.
│   │   ├── `create_initial_population(environment, initial_genes=None)`: Creates an initial population of agents with randomly generated genomes, if `initial_genes` is none.
│   │   ├── `selection(agents, environment)`: Selects the fittest agents from the current population based on their survival time and resource collection.
│   │   ├── `crossover(parent1, parent2)`: Performs crossover between two parent agents, creating two new offspring agents.
│   │   ├── `mutation(agent)`: Mutates the genome of an agent, randomly changing gene values.
│   │   └── `evolve(agents, environment)`: Performs one generation of the genetic algorithm, creating a new population of agents from the previous generation.
│   ├── selection.py    (Selection methods)
│   │   ├── `tournament_selection(agents, tournament_size)`: Selects an agent using tournament selection, where agents compete against each other, and the winner is selected.
│   │   ├── `roulette_wheel_selection(agents)`: Selects an agent using roulette wheel selection, where agents are selected based on their fitness.
│   │   └── `rank_selection(agents)`: Selects agents based on their rank.
│   ├── crossover.py    (Crossover methods)
│   │   ├── `single_point_crossover(parent1, parent2)`: Performs single-point crossover between two parent agents, creating two new offspring agents.
│   │   ├── `two_point_crossover(parent1, parent2)`: Performs two-point crossover between two parent agents, creating two new offspring agents.
│   │   └── `uniform_crossover(parent1, parent2)`: Performs uniform crossover between two parent agents, creating two new offspring agents.
│   └── mutation.py     (Mutation methods)
│       ├── `gaussian_mutation(agent, mutation_rate)`: Mutates the genome of an agent by adding a random value from a Gaussian distribution to each gene.
│       ├── `uniform_mutation(agent, mutation_rate)`: Mutates the genome of an agent by replacing each gene with a random value from a uniform distribution.
│       └── `bit_flip_mutation(agent, mutation_rate)`: Mutates the genome of an agent by flipping a random bit in each gene.
├── rl/               (Reinforcement Learning Code)
│   ├── __init__.py   (Makes the rl directory a Python package)
│   ├── model.py        (Definition of the RNN model)
│   │   ├── `__init__(input_size, hidden_size, output_size)`: Initializes the RNN model with given input, hidden, and output sizes.
│   │   ├── `forward(state)`: Performs a forward pass through the RNN model, returning action probabilities.
│   │   └── `save(path)`: Saves the model to a file.
│   ├── agent.py        (Agent for reinforcment learning and how to interact with the environment)
│   │   ├── `__init__(environment, model, learning_rate, discount_factor)`: Initializes the reinforcement learning agent with a given environment, model, learning rate, and discount factor.
│   │   ├── `select_action(state)`: Selects an action based on the current state using the model.
│   │   ├── `step(action)`: Takes a step in the environment based on the selected action, returning the next state, reward, and done flag.
│   │   ├── `learn(state, action, reward, next_state, done)`: Updates the model based on the observed reward.
│   │   └── `save_model(path)`: Saves the model to a file.
│   ├── training.py     (Code to train the agent)
│   │   ├── `train(environment, agent, num_episodes)`: Trains the reinforcement learning agent in the given environment for a specified number of episodes.
│   │   ├── `calculate_reward(agent, environment)`: Calculates the reward for the agent based on its actions and the state of the environment.
│   │   └── `evaluate(environment, agent, num_episodes)`: Evaluates the performance of the trained agent in the given environment.
│   └── utils.py        (Helper functions for RL)
│       ├── `normalize_state(state)`: Normalizes the state vector to improve training.
│       ├── `discount_rewards(rewards, discount_factor)`: Discounts the rewards to give more weight to earlier rewards.
│       └── `one_hot_encode(action, num_actions)`: One-hot encodes the action to be used as input to the neural network.
├── visualization/   (Code related to Primer.py or other visualization)
│   ├── __init__.py   (Makes the visualization directory a Python package)
│   ├── primer_vis.py  (Visualization code using Primer.py)
│   │   ├── `initialize_scene()`: Initializes the Primer.py scene, creating the terrain, resources, and agents.
│   │   ├── `update_scene(environment, agents)`: Updates the Primer.py scene based on the current state of the environment and the agents.
│   │   ├── `draw_terrain(terrain)`: Draws the terrain in the Primer.py scene.
│   │   ├── `draw_resources(resource_map)`: Draws the resources in the Primer.py scene.
│   │   └── `draw_agents(agents)`: Draws the agents in the Primer.py scene.
│   └── utils.py        (Helper functions for visualizations)
│       ├── `convert_terrain_to_mesh(terrain)`: Converts the terrain heightmap to a mesh that can be rendered in Primer.py.
│       └── `create_agent_mesh(agent)`: Creates a mesh representing an agent in Primer.py.
├── utils/            (General utility functions)
│   ├── __init__.py   (Makes the utils directory a Python package)
│   ├── data_logging.py (Data logging functions)
│   │   ├── `log_data(data, filename)`: Logs data to a file (CSV, JSON, etc.).
│   │   ├── `load_data(filename)`: Loads data from a file.
│   │   └── `visualize_data(filename)`: Visualizes data using Matplotlib or other libraries.
│   └── math_utils.py   (General purpose math functions)
│       ├── `distance(x1, y1, x2, y2)`: Calculates the distance between two points.
│       ├── `normalize(value, min_value, max_value)`: Normalizes a value to a range between 0 and 1.
│       └── `clamp(value, min_value, max_value)`: Clamps a value to a given range.
└── main.py          (Main simulation loop)
    ├── `main()`:  The main function that initializes the environment, creates the agents, runs the simulation, and visualizes the results.  This function orchestrates all the components of the simulation.