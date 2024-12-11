import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import random
import numpy as np
import numpy as np
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
# Include your classes (Family, StochasticVectorField2D, City, etc.) here

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

            direction = np.array([f.x - self.family.x, f.y - self.family.y])
            distance = np.linalg.norm(direction)
            if distance == 0:
                continue
            direction = direction / distance
            effect = 1.0 / (distance**2 + 1e-6)

            if (f.race == "black" and self.family.race == "white"):
                vector -= 0.001 * effect * direction
            if (f.race == "white" and self.family.race == "white"):
                vector += 0.0001 * effect * direction

            if (f.race == "black" and self.family.race == "black"):
                vector += 0.0000
            if (f.race == "white" and self.family.race == "black"):
                vector += 0.00005 * effect * direction

            vector += np.random.normal(0, 0.05, 2)

        center = self.city.city_boundary.centroid
        center_x, center_y = center.x, center.y

        direction = np.array([center_x - self.family.x, center_y - self.family.y])
        distance = np.linalg.norm(direction)
        if distance == 0:
            return vector
        direction = direction / distance

        effect = 1.0 / (distance**2 + 1e-6)
        vector += 0.001 * effect * direction

        return vector

class City:
    def __init__(self, wp, bp, city_boundary, min_distance=1.0, max_step_size=0.1):
        self.wp = wp
        self.bp = bp
        self.families = {}
        self.city_boundary = city_boundary
        self.min_distance = min_distance
        self.max_step_size = max_step_size

    def populate(self):
        centroid = self.city_boundary.centroid
        center_x, center_y = centroid.x, centroid.y

        for i in range(self.wp):
            id = f"w{i}"
            x, y = self.random_position_near_center(center_x, center_y)
            family = Family("white", x, y)
            self.families[id] = family

        for i in range(self.bp):
            id = f"b{i}"
            x, y = self.random_position_near_center(center_x, center_y)
            family = Family("black", x, y)
            self.families[id] = family

    def random_position_near_center(self, center_x, center_y):
        while True:
            x_offset = random.uniform(-0.05, 0.05)
            y_offset = random.uniform(-0.05, 0.05)
            x = center_x + x_offset
            y = center_y + y_offset
            point = Point(x, y)
            if self.city_boundary.contains(point):
                return x, y

    def step(self):
        for family in self.families.values():
            vf = StochasticVectorField2D(self, family)
            vector = vf.compute_vector()

            new_x = family.x + vector[0]
            new_y = family.y + vector[1]

            distance = np.linalg.norm([new_x - family.x, new_y - family.y])
            if distance > self.max_step_size:
                scale_factor = self.max_step_size / distance
                new_x = family.x + vector[0] * scale_factor
                new_y = family.y + vector[1] * scale_factor

            if not self.city_boundary.contains(Point(new_x, new_y)):
                new_x, new_y = self.keep_within_bounds(new_x, new_y)

            family.x = new_x
            family.y = new_y

    def keep_within_bounds(self, new_x, new_y):
        point = Point(new_x, new_y)
        if self.city_boundary.contains(point):
            return new_x, new_y
        else:
            nearest_point = nearest_points(point, self.city_boundary.boundary)[1]
            return nearest_point.x, nearest_point.y

    def plot_grid(self):
        plt.figure(figsize=(6, 6))
        white_x = []
        white_y = []
        black_x = []
        black_y = []

        for family in self.families.values():
            if family.race == "white":
                white_x.append(family.x)
                white_y.append(family.y)
            else:
                black_x.append(family.x)
                black_y.append(family.y)

        plt.scatter(white_x, white_y, color='orange', label="White Families", s=50)
        plt.scatter(black_x, black_y, color='black', label="Black Families", s=50)

        x, y = self.city_boundary.exterior.xy
        plt.plot(x, y, color='red', linewidth=2, label="City Boundary")

        plt.xlim(self.city_boundary.bounds[0], self.city_boundary.bounds[2])
        plt.ylim(self.city_boundary.bounds[1], self.city_boundary.bounds[3])
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Family Positions in the City')
        plt.legend()
        st.pyplot(plt)


def main():
    st.title("City Simulation")
    shapefile_path = "ex_gis/cb_2018_us_csa_500k.shp"
    gdf = gpd.read_file(shapefile_path)
    city_names = gdf['NAME'].tolist()
    city_name = st.sidebar.selectbox("City Name", city_names)
    city_num = city_names.index(city_name)
    city_boundary = gdf.geometry.iloc[city_num]

    white_population = st.sidebar.slider("White Population", min_value=100, max_value=1000, value=400)
    black_population = st.sidebar.slider("Black Population", min_value=10, max_value=200, value=20)
    min_distance = st.sidebar.slider("Min Distance", min_value=0.0, max_value=2.0, value=0.1)
    max_step_size = st.sidebar.slider("Max Step Size", min_value=0.01, max_value=1.0, value=0.1)
    steps = st.sidebar.slider("Simulation Steps", min_value=1, max_value=50, value=10)

    if st.button("Run Simulation"):
        city = City(white_population, black_population, city_boundary, min_distance, max_step_size)
        city.populate()

        for _ in range(steps):
            city.step()

        city.plot_grid()

if __name__ == "__main__":
    main()
