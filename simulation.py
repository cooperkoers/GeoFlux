import geopandas as gpd
import streamlit as st

from src.GeoFlux.city import City

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

    city.plot_grid()
