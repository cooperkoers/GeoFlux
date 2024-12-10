import numpy as np
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points

class StochasticVectorField2D:
    def __init__(self, city, family):
        self.city = city
        self.family = family

    def compute_vector(self):
        vector = np.array([0.0, 0.0])
        for f in self.city.families.values():
            if f == self.family:
                continue

            # Find direction and distance to other families
            direction = np.array([f.x - self.family.x, f.y - self.family.y])
            distance = np.linalg.norm(direction)
            if distance == 0:  # Avoid division by zero
                continue
            direction = direction / distance

            # Inverse square law for stronger effects
            effect = 1.0 / (distance**2 + 1e-6)

            # Apply different rules based race
            if (f.race == "black" and self.family.race == "white"):
                vector -= 0.001 * effect * direction  # Weak repulsion
            if (f.race == "white" and self.family.race == "white"):
                vector += 0.0001 * effect * direction  # Weak attraction

            if (f.race == "black" and self.family.race == "black"):
                vector += 0.0000  # Neutral to other black families
            if (f.race == "white" and self.family.race == "black"):
                vector += 0.00005 * effect * direction  # Weak attraction to white families

            # Add noise for more realistic movement
            vector += np.random.normal(0, 0.05, 2)  # Lower noise
        
        # add small bias to move towards the center TODO: Check to see if thus is the correct way to do this
        # TODO: review if needed in model
        center = self.city.city_boundary.centroid
        center_x, center_y = center.x, center.y
        
        direction = np.array([center_x - self.family.x, center_y - self.family.y])
        distance = np.linalg.norm(direction)
        if distance == 0:  # Avoid division by zero
            return vector
        direction = direction / distance

        effect = 1.0 / (distance**2 + 1e-6)
        vector += 0.001 * effect * direction

        return vector
