import random
from shapely.geometry import Point
from shapely.ops import nearest_points
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from .family import Family
from .stochastic_vector_field import StochasticVectorField2D

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

    def plot_grid(self, step_num, city_name):
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

        plt.scatter(white_x, white_y, color='orange', label="Majority Families", s=50)
        plt.scatter(black_x, black_y, color='black', label="Minority Families", s=50)

        x, y = self.city_boundary.exterior.xy
        plt.plot(x, y, color='red', linewidth=2, label="City Boundary")

        plt.xlim(self.city_boundary.bounds[0], self.city_boundary.bounds[2])
        plt.ylim(self.city_boundary.bounds[1], self.city_boundary.bounds[3])
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title(f"Family Positions in {city_name} at Step {step_num}")
        plt.legend()
        st.pyplot(plt)
