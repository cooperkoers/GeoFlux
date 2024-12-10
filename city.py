import numpy as np
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from family import Family
from stochastic_vector_field import StochasticVectorField2D

class City:
    def __init__(self, wp, bp, city_boundary, min_distance=1.0, max_step_size=0.1):
        self.wp = wp
        self.bp = bp
        self.families = {}
        self.city_boundary = city_boundary  # Polygon representing the city boundary
        self.min_distance = min_distance  # Minimum distance constraint
        self.max_step_size = max_step_size  # Maximum step size constraint

    def populate(self):
        # Get the centroid of the city (polygon)
        centroid = self.city_boundary.centroid
        center_x, center_y = centroid.x, centroid.y

        # Populate white families around the center
        for i in range(self.wp):
            id = f"w{i}"
            x, y = self.random_position_near_center(center_x, center_y)
            family = Family("white", x, y)
            self.families[id] = family

        # Populate black families around the center
        for i in range(self.bp):
            id = f"b{i}"
            x, y = self.random_position_near_center(center_x, center_y)
            family = Family("black", x, y)
            self.families[id] = family

    def random_position_near_center(self, center_x, center_y):
        """Generate a random position near the center within the city boundary."""
        while True:
            # Generate random x, y coordinates near the centroid
            x_offset = random.uniform(-0.05, 0.05)  # Spread out by a small random amount
            y_offset = random.uniform(-0.05, 0.05)  # Spread out by a small random amount
            x = center_x + x_offset
            y = center_y + y_offset
            point = Point(x, y)
            print(f"point {point}")
            # Check if the generated point is inside the boundary
            if self.city_boundary.contains(point):
                return x, y

    def is_too_close(self, family, new_x, new_y):
        """Check if the new position is too close to any other family."""
        for other in self.families.values():
            if other == family:
                continue
            distance = np.linalg.norm([new_x - other.x, new_y - other.y])
            if distance < self.min_distance:
                return True
        return False

    def step(self):
        # Update positions based on vector field
        for family in self.families.values():
            print(f"location of family {family.x}, {family.y}")
            vf = StochasticVectorField2D(self, family)
            vector = vf.compute_vector()
            print(f"change of family {vector[0]}, {vector[1]}")
            
            # Propose new position
            new_x = family.x + vector[0]
            new_y = family.y + vector[1]

            # Limit the movement (capping the maximum step size)
            distance = np.linalg.norm([new_x - family.x, new_y - family.y])
            if distance > self.max_step_size:
                # Scale the vector to the maximum step size
                scale_factor = self.max_step_size / distance
                new_x = family.x + vector[0] * scale_factor
                new_y = family.y + vector[1] * scale_factor

            # Check if the new position is too close to other families
            if not self.is_too_close(family, new_x, new_y):
                # Adjust the movement to stay within bounds
                if not self.city_boundary.contains(Point(new_x, new_y)):
                    # Calculate the best fitting vector that stays inside the boundary
                    new_x, new_y = self.keep_within_bounds(new_x, new_y)
                family.x = new_x
                family.y = new_y

            # Optional: Ensure positions stay within grid bounds
            family.x = np.clip(family.x, self.city_boundary.bounds[0], self.city_boundary.bounds[2])
            family.y = np.clip(family.y, self.city_boundary.bounds[1], self.city_boundary.bounds[3])

        # Plot the city grid with families
        self.plot_grid()

    def keep_within_bounds(self, new_x, new_y):
        # Ensure the new position is within the city boundary
        point = Point(new_x, new_y)
        if self.city_boundary.contains(point):
            return new_x, new_y
        else:
            # Use nearest_points to find the closest point on the boundary
            nearest_point = nearest_points(point, self.city_boundary.boundary)[1]
            return nearest_point.x, nearest_point.y

    def plot_grid(self):
        # Plot family positions using scatter
        plt.figure(figsize=(6, 6))
        white_x = []
        white_y = []
        black_x = []
        black_y = []

        # Separate families by race
        for family in self.families.values():
            if family.race == "white":
                white_x.append(family.x)
                white_y.append(family.y)
            else:
                black_x.append(family.x)
                black_y.append(family.y)

        # Plot the positions with specified colors
        plt.scatter(white_x, white_y, color='orange', label="White Families", s=50)
        plt.scatter(black_x, black_y, color='black', label="Black Families", s=50)

        # Plot the city boundary (polygon)
        x, y = self.city_boundary.exterior.xy
        plt.plot(x, y, color='red', linewidth=2, label="City Boundary")

        # Set grid limits and labels
        plt.xlim(self.city_boundary.bounds[0], self.city_boundary.bounds[2])
        plt.ylim(self.city_boundary.bounds[1], self.city_boundary.bounds[3])
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Family Positions in the City')
        plt.legend()

        # Show the plot
        plt.show()