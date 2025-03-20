# river_generation.py
import random
import numpy as np
from .terrain import TERRAIN_WATER, TERRAIN_GRASS
import math

def update_water(terrain, terrain_type_map, water_flow, water_dryness, dt, dryness_threshold=5.0, erosion_rate=0.0005, diffusion_rate=0.1, momentum=0.5):
    """
    Updates water flow, dryness, and erodes terrain under water cells.
    Includes water flow diffusion and momentum.
    """
    h, w = terrain.shape

    # 1. Compute flow vectors: Follow steepest descent.
    new_flow = np.zeros_like(water_flow)  # Store new flow vectors here.

    for y in range(h):
        for x in range(w):
            if terrain_type_map[y, x] == TERRAIN_WATER:
                current_height = terrain[y, x]
                best_x, best_y = x, y
                best_height = current_height

                # Check neighboring cells for the steepest descent.
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            nh = terrain[ny, nx]
                            if nh < best_height:
                                best_height = nh
                                best_x, best_y = nx, ny

                # Compute the new flow vector.
                dx = best_x - x
                dy = best_y - y
                length = np.hypot(dx, dy)
                if length > 0:
                    vx = dx / length
                    vy = dy / length
                    # Scale speed by the height difference.
                    speed = (current_height - best_height) * 1.0
                    new_flow[y, x] = (vx * speed, vy * speed)
                else:
                    new_flow[y, x] = (0, 0)  # No descent possible.
            else:
                new_flow[y, x] = (0, 0)  # Non-water cells have no flow.

    # 2. Diffusion:  Blend the flow vectors with neighbors to simulate diffusion.
    diffused_flow = np.zeros_like(water_flow)
    for y in range(h):
        for x in range(w):
            total_flow = np.array([0.0, 0.0])
            count = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        total_flow += new_flow[ny, nx]
                        count += 1
            if count > 0:
                average_flow = total_flow / count
                diffused_flow[y, x] = (1 - diffusion_rate) * new_flow[y, x] + diffusion_rate * average_flow

    # 3. Apply Momentum: Combine new flow with the previous flow.
    for y in range(h):
        for x in range(w):
            if terrain_type_map[y, x] == TERRAIN_WATER:
                water_flow[y, x] = (momentum * water_flow[y, x][0] + (1 - momentum) * diffused_flow[y, x][0],
                                     momentum * water_flow[y, x][1] + (1 - momentum) * diffused_flow[y, x][1])
            else:
                water_flow[y, x] = (0, 0)
    # 4. Update dryness and erosion:
    for y in range(h):
        for x in range(w):
            if terrain_type_map[y, x] == TERRAIN_WATER:
                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            if terrain_type_map[ny, nx] == TERRAIN_WATER:
                                count += 1
                if count < 2:
                    water_dryness[y, x] += dt
                    if water_dryness[y, x] > dryness_threshold:
                        # Dry up: convert cell to grass.
                        terrain_type_map[y, x] = TERRAIN_GRASS
                        water_flow[y, x] = (0, 0)
                        water_dryness[y, x] = 0
                        continue
                else:
                    water_dryness[y, x] = 0

                # Erode the terrain slightly under water.
                terrain[y, x] = max(0.0, terrain[y, x] - erosion_rate * dt)
            else:
                water_flow[y, x] = (0, 0)
                water_dryness[y, x] = 0

def carve_river(heightmap, terrain_type_map, start, river_smooth_radius, branch_probability=0.2, min_length=10, visited=None):
    """
    Carves a river path from a given start point by following steepest descent, with smoothing.
    Marks cells in terrain_type_map as TERRAIN_WATER.
    """
    if visited is None:
        visited = set()
    path = []
    current = start
    while True:
        x, y = current
        if current in visited:
            break
        visited.add(current)

        # If we've moved from the source and are at the border, stop the river.
        if (x == 0 or y == 0 or x == heightmap.shape[1] - 1 or y == heightmap.shape[0] - 1) and len(path) > 1:
            break

        # Get 8-connected neighbors.
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < heightmap.shape[1] and 0 <= ny < heightmap.shape[0]:
                    neighbors.append((nx, ny))
        current_height = heightmap[y, x]
        lower_neighbors = [pos for pos in neighbors if heightmap[pos[1], pos[0]] < current_height]
        if not lower_neighbors:
            break  # No descent possible

        # Choose the neighbor with the lowest height.
        next_cell = min(lower_neighbors, key=lambda pos: heightmap[pos[1], pos[0]])

        # Branching: if other neighbors are nearly as low, possibly start a branch.
        threshold = 0.02  # Height difference threshold for branching.
        min_height = heightmap[next_cell[1], next_cell[0]]
        candidate_branches = [
            pos for pos in lower_neighbors
            if abs(heightmap[pos[1], pos[0]] - min_height) < threshold and pos != next_cell
        ]
        if candidate_branches and len(path) >= min_length:
            if random.random() < branch_probability:
                branch_start = candidate_branches[0]
                carve_river(heightmap, terrain_type_map, branch_start, river_smooth_radius, branch_probability, min_length, visited)

        # Apply smoothing around the river point
        for i in range(-river_smooth_radius, river_smooth_radius + 1):
            for j in range(-river_smooth_radius, river_smooth_radius + 1):
                carve_x, carve_y = x + i, y + j
                if 0 <= carve_x < heightmap.shape[1] and 0 <= carve_y < heightmap.shape[0]:
                    dist = math.hypot(i, j)  # Distance from center
                    if dist <= river_smooth_radius:
                        # Calculate smoothing factor (0.0 at edge, 1.0 at center)
                        smooth_factor = 1 - (dist / river_smooth_radius)
                        # Apply smooth height reduction
                        height_reduction = 0.1 * smooth_factor  # Adjust reduction as needed
                        heightmap[carve_y, carve_x] = min(heightmap[carve_y, carve_x], heightmap[carve_y, carve_x] * (1 - height_reduction))  # Smoothly reduce height
                        terrain_type_map[carve_y, carve_x] = TERRAIN_WATER

        path.append(current)

        current = next_cell
    return path

def add_rivers(heightmap, terrain_type_map):
    """Temporarily disabled river generation while keeping the function structure."""
    h, w = heightmap.shape
    water_flow = np.zeros((h, w, 2), dtype=np.float32)  # Store flow vectors (x, y)
    water_dryness = np.zeros((h, w), dtype=np.float32)  # Track how long water has been isolated
    
    # Return empty water flow and dryness maps without modifying the terrain
    return water_flow, water_dryness