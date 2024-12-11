import numpy as np
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
import streamlit as st


class Family:
    def __init__(self, race, x, y):
        self.race = race
        self.x = x
        self.y = y

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
                vector += 0.00005  # Neutral to other black families
            if (f.race == "white" and self.family.race == "black"):
                vector += 0.00005 * effect * direction  # Weak attraction to white families

            # Add noise for more realistic movement
            vector += np.random.normal(0, 0.05, 2)  # Lower noise

        return vector

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
            x_offset = random.uniform(-0.1, 0.1)  # Spread out by a small random amount
            y_offset = random.uniform(-0.1, 0.1)  # Spread out by a small random amount
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
        plt.scatter(white_x, white_y, color='orange', label="White Families", s=100)
        plt.scatter(black_x, black_y, color='black', label="Black Families", s=100)

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


# Read the shapefile for the city boundary (make sure to adjust the file path)
#shapefile_path = "ex_gis/cb_2018_us_csa_500k.shp"
#gdf = gpd.read_file(shapefile_path)

# Assume you want to use the first polygon as the city boundary
#city_boundary = gdf.geometry.iloc[1]
#print(city_boundary)

# Simulation
#white_population = 100
#black_population = 50
#min_distance = 0  # Minimum distance between families

#city = City(white_population, black_population, city_boundary, min_distance)
#city.populate()
#city.plot_grid()

# Run simulation for a few steps
#for _ in range(50):
#    city.step()

# Adaptation for Streamlit
def run_simulation(white_population, black_population, steps, min_distance, max_step_size, shapefile_path, polygon_index):
    # Read the shapefile for the city boundary
    gdf = gpd.read_file(shapefile_path)
    city_boundary = gdf.geometry.iloc[polygon_index]

    # Initialize the city
    city = City(white_population, black_population, city_boundary, min_distance, max_step_size)
    city.populate()

    # Run simulation for the specified number of steps
    for _ in range(steps):
        city.step()

    return city

def main():
    st.title("City Simulation: Stochastic Vector Field with Family Interaction")

    # Sidebar inputs for user control
    st.sidebar.header("Simulation Parameters")
    white_population = st.sidebar.slider("White Population", min_value=10, max_value=1000, value=400, step=10)
    black_population = st.sidebar.slider("Black Population", min_value=10, max_value=1000, value=50, step=10)
    steps = st.sidebar.slider("Simulation Steps", min_value=1, max_value=100, value=10, step=1)
    min_distance = st.sidebar.slider("Minimum Distance", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
    max_step_size = st.sidebar.slider("Max Step Size", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    polygon_index = st.sidebar.number_input("Polygon Index (City Boundary)", min_value=0, max_value=100, value=10)

    # File upload for shapefile
    shapefile_path = st.sidebar.text_input("Shapefile Path", "ex_gis/cb_2018_us_csa_500k.shp")

    # Run simulation when user clicks the button
    if st.sidebar.button("Run Simulation"):
        try:
            city = run_simulation(white_population, black_population, steps, min_distance, max_step_size, shapefile_path, polygon_index)

            # Plot the final grid
            st.pyplot(city.plot_grid())
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
