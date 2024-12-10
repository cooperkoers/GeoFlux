import numpy as np
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
import streamlit as st

from family import Family
from city import City

def sim(city_num, white_population, black_population, min_distance, num_steps):
    # Load city boundary
    shapefile_path = "ex_gis/cb_2018_us_csa_500k.shp"
    gdf = gpd.read_file(shapefile_path)

    # Assume you want to use the polygon as the city boundary
    city_boundary = gdf.geometry.iloc[city_num]

    city = City(white_population, black_population, city_boundary, min_distance)
    city.populate()
    city.plot_grid()

    # Run simulation for n steps
    for _ in range(num_steps):
        city.step()
    

shapefile_path = "ex_gis/cb_2018_us_csa_500k.shp"
gdf = gpd.read_file(shapefile_path)

# Assume you want to use the first polygon as the city boundary
city_boundary = gdf.geometry.iloc[49]
print(city_boundary)

# Simulation
white_population = 400
black_population = 50
min_distance = 0  # Minimum distance between families

city = City(white_population, black_population, city_boundary, min_distance)
city.populate()
city.plot_grid()

# Run simulation for a few steps
for _ in range(50):
    city.step()