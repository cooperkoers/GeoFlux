import streamlit as st
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Generate some data for the graph
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Save the plot as an image
fig, ax = plt.subplots()
ax.plot(x, y, label="Sine Wave")
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_title("Draw on the Plot")
ax.legend()

# Save the plot to an image file
fig.savefig("background_plot.png")
plt.close(fig)

# Load the saved plot as an image
bg_image = Image.open("background_plot.png")

# Display instructions
st.title("Draw on a Plot with Background")
st.write("Draw on the canvas to interact with the graph!")

# Add the drawable canvas with the plot as the background
canvas_result = st_canvas(
    stroke_width=2,
    stroke_color="#000000",
    background_image=bg_image,  # Use the saved plot as the background
    height=bg_image.height,  # Match the canvas size to the image
    width=bg_image.width,
    drawing_mode="freedraw",
    key="canvas_with_plot",
)

# Extract drawn points and map them to graph coordinates
if canvas_result.json_data is not None:
    points_list = []

    # Extract objects from canvas JSON data
    objects = canvas_result.json_data["objects"]
    for obj in objects:
        if obj["type"] == "path":
            # Path contains a series of points [x, y, ...]
            path = obj["path"]
            for coord in path:
                if isinstance(coord, list) and len(coord) >= 2:
                    # Capture x, y values
                    points_list.append((coord[0], coord[1]))
    
    # Display the collected points
    if points_list:
        st.write("Points touched on the canvas:")
        st.write(points_list)

        # Save the points into a list of graph coordinates
        graph_points = []
        canvas_width, canvas_height = bg_image.width, bg_image.height
        x_min, x_max = 0, 10  # The x-range of the plot
        y_min, y_max = -1, 1  # The y-range of the sine wave plot

        for cx, cy in points_list:
            # Map canvas coordinates to graph coordinates
            gx = x_min + (float(cx) / canvas_width) * (x_max - x_min)
            gy = y_max - (float(cy) / canvas_height) * (y_max - y_min)
            graph_points.append((gx, gy))

        st.write("Mapped points on the graph:")
        st.write(graph_points)
else:
    st.write("No drawing detected yet.")
