import pandas as pd
import numpy as np
from geopy.distance import geodesic
import folium
import itertools

# Step 1: Import the data from the CSV file
file_path = '/mnt/c/Users/jodie/Downloads/nodes.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Step 2: Group the data by cluster
clusters = df.groupby('cluster')

# Parameters for the ACO
num_ants = 10
iterations = 100
alpha = 1.0  # Importance of pheromone
beta = 2.0  # Importance of heuristic information (distance)
evaporation_rate = 0.5
initial_pheromone = 1.0

# Compute the distance matrix
def compute_distance_matrix(locations):
    dist_matrix = np.zeros((len(locations), len(locations)))
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:
                dist_matrix[i][j] = geodesic(loc1, loc2).meters
    return dist_matrix

# Ant class to construct solutions
class Ant:
    def __init__(self, num_locations):
        self.num_locations = num_locations
        self.visited = set()
        self.route = []

    def visit_location(self, location):
        self.visited.add(location)
        self.route.append(location)

    def is_visited(self, location):
        return location in self.visited

    def get_route_length(self):
        length = 0.0
        for i in range(len(self.route) - 1):
            length += distance_matrix[self.route[i]][self.route[i+1]]
        # Return to the depot
        length += distance_matrix[self.route[-1]][depot_index]
        return length

# ACO algorithm
def aco(num_ants, iterations, alpha, beta, evaporation_rate):
    global pheromones

    best_route = None
    best_route_length = float('inf')

    for _ in range(iterations):
        ants = [Ant(num_locations) for _ in range(num_ants)]

        for ant in ants:
            ant.visit_location(depot_index)

            while len(ant.route) < num_locations:
                current_location = ant.route[-1]
                probabilities = []

                for next_location in range(num_locations):
                    if not ant.is_visited(next_location):
                        tau = pheromones[current_location][next_location] ** alpha
                        eta = (1.0 / distance_matrix[current_location][next_location]) ** beta
                        probabilities.append((next_location, tau * eta))

                if not probabilities:
                    break

                total = sum(prob for _, prob in probabilities)
                probabilities = [(loc, prob / total) for loc, prob in probabilities]

                next_location = np.random.choice(
                    [loc for loc, _ in probabilities],
                    p=[prob for _, prob in probabilities]
                )
                ant.visit_location(next_location)

        # Update pheromones
        pheromones *= (1.0 - evaporation_rate)

        for ant in ants:
            route_length = ant.get_route_length()
            if route_length < best_route_length:
                best_route_length = route_length
                best_route = ant.route

            for i in range(len(ant.route) - 1):
                pheromones[ant.route[i]][ant.route[i + 1]] += 1.0 / route_length
            pheromones[ant.route[-1]][depot_index] += 1.0 / route_length

    return best_route, best_route_length

# Create a folium map centered at the average location
map_center = [df['lat'].mean(), df['long'].mean()]
mymap = folium.Map(location=map_center, zoom_start=13)

colors = itertools.cycle(['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                          'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 
                          'lightblue', 'lightgreen', 'gray', 'black'])

# Process each cluster separately
for cluster_id, cluster_data in clusters:
    # Extract the coordinates
    locations = cluster_data[['lat', 'long']].values.tolist()
    
    # Define the depot (starting point)
    depot_index = 0

    distance_matrix = compute_distance_matrix(locations)
    num_locations = len(locations)

    # Initialize pheromones
    pheromones = np.ones((num_locations, num_locations)) * initial_pheromone

    # Run ACO for the current cluster
    best_route, best_route_length = aco(num_ants, iterations, alpha, beta, evaporation_rate)

    # Convert the route to readable format
    optimized_route = [locations[node] for node in best_route]

    print(f"Cluster {cluster_id}: Best route: {optimized_route}")
    print(f"Cluster {cluster_id}: Best route length: {best_route_length} meters")


    cluster_color = next(colors)

    # Add markers for each location
    for i, loc in enumerate(locations):
        popup_text = f"Cluster: {cluster_id}, Latitude: {loc[0]}, Longitude: {loc[1]}"
        folium.Marker(location=loc, popup=popup_text, icon=folium.Icon(color=cluster_color)).add_to(mymap)
        
    # Add a line for the optimized route
    folium.PolyLine(locations=optimized_route, color=cluster_color, weight=2.5, opacity=1).add_to(mymap)

# Save the map to an HTML file
mymap.save('optimized_patrol_routes.html')
