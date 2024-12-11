import numpy as np

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
