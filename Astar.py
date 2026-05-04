#Import (Setup)
import requests
from math import radians, sin, cos, sqrt, atan2
from collections import defaultdict
import heapq
import folium



def user_input():
    starting_pos = input("Enter your starting geo-coordinate: ").split(",")
    s_lat, s_lon = float(starting_pos[0]), float(starting_pos[1])

    destination_pos = input("Enter your desination's geo-coordinate: ").split(",")
    d_lat, d_lon = float(destination_pos[0]), float(destination_pos[1])

    return s_lat, s_lon, d_lat, d_lon

def haversine(s_lat, s_lon, d_lat, d_lon):
    R = 6371.0 # Earth radius in km

    # Convert decimal degrees to radians
    delta_lat = radians(s_lat - d_lat)
    delta_lon = radians(s_lon - d_lon)
    
    a = sin(delta_lat/2)**2 + cos(radians(s_lat)) * cos(radians(d_lat)) * sin(delta_lon/2)**2 
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c * 1000


def midpoint(s_lat, s_lon, d_lat, d_lon):
    mid_lat = (s_lat + d_lat) / 2
    mid_lon = (s_lon + d_lon) / 2
    radius = haversine(mid_lat, mid_lon, s_lat, s_lon)


    return mid_lat, mid_lon, max(radius * 1.5, 2000) #Standarize map scale

def fetch_graph(mid_lat, mid_lon, radius):
    graph = defaultdict(list)
    
    url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    way
    [highway]
    [highway !~ "motorway|motorway_link|trunk"]
    
    
    (around:{radius},{mid_lat}, {mid_lon});
    out body;
    >;
    out skel qt;
    """

    
    headers = {
        'User-Agent': 'WalkingPathFinder/1.0 (your-email@gmail.com)',
        'Accept': 'application/json'
    }

    response = requests.get(url, params={'data': query}, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    elements = data.get('elements', [])

    node_lookup = {e['id']: e for e in elements if e['type'] == 'node'}
    ways = [e for e in elements if e['type'] == 'way']

    # Process and create roads and find intersections
    for way in ways:
        node_ids = way.get('nodes', [])
        
        for i in range(len(node_ids) - 1):
            id1 = node_ids[i]
            id2 = node_ids[i+1]
            
            n1 = node_lookup.get(id1)
            n2 = node_lookup.get(id2)
            
            if n1 and n2:
                dist = haversine(n1['lat'], n1['lon'], n2['lat'], n2['lon'])
                
                # Store bi-directionally
                graph[id1].append((id2, round(dist, 2)))
                graph[id2].append((id1, round(dist, 2)))


    return graph, node_lookup

    


def nearest_nodes(lat, lon, node_lookup, graph, limit=25):
    candidates = []

    for node_id, node in node_lookup.items():
        if not graph.get(node_id):
            continue
        distance = haversine(lat, lon, node['lat'], node['lon'])
        candidates.append((distance, node_id))

    candidates.sort()
    return [node_id for _, node_id in candidates[:limit]]


def astar(graph,start,goal,node_lookup):
    if start is None or goal is None:
        return None

    heap = []
    heapq.heappush(heap,(0,start))
    came_from = {}
    g_scores = {start: 0}
    visited = set()
    

    while heap:
        current_f, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == goal:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start)
            return path[::-1]
        
        for neighbor, distance in graph[current_node]:
            
            new_g = g_scores[current_node] + distance
            
            if neighbor not in g_scores or new_g < g_scores[neighbor]:
                g_scores[neighbor] = new_g
                
                # Calculate h: straight line distance to goal
                n = node_lookup[neighbor]
                goal_node = node_lookup[goal]
                h = haversine(n['lat'], n['lon'], goal_node['lat'], goal_node['lon'])
                
                f = new_g + h
                heapq.heappush(heap, (f, neighbor))
                came_from[neighbor] = current_node
    return None  # No path found

def find_path(graph, node_lookup, s_lat, s_lon, d_lat, d_lon):
    start_candidates = nearest_nodes(s_lat, s_lon, node_lookup, graph)
    goal_candidates = nearest_nodes(d_lat, d_lon, node_lookup, graph)

    for start in start_candidates:
        for goal in goal_candidates:
            path = astar(graph, start, goal, node_lookup)
            if path:
                return start, goal, path

    return (
        start_candidates[0] if start_candidates else None,
        goal_candidates[0] if goal_candidates else None,
        None,
    )

def visualize_data(path,node_lookup):
    coords = []
    for paths in path:
        node = node_lookup[paths]
        coords.append([node['lat'], node['lon']])    
    return coords 

def main():
    s_lat, s_lon, d_lat, d_lon = user_input()
    mid_lat, mid_lon, radius = midpoint(s_lat, s_lon, d_lat, d_lon)

    try:
        graph, node_lookup = fetch_graph(mid_lat, mid_lon, radius)
    except requests.RequestException as error:
        print(f"Could not fetch map data from Overpass: {error}")
        return
    start, goal, path = find_path(graph, node_lookup, s_lat, s_lon, d_lat, d_lon)

    print("Start node:", start)
    print("Goal node:", goal)
    print("Start in graph:", start in graph if start is not None else False)
    print("Goal in graph:", goal in graph if goal is not None else False)
    print("Graph size:", len(graph))

    if start is not None:
        print("Start neighbors:", graph[start])
    if goal is not None:
        print("Goal neighbors:", graph[goal])

    if path is None:
        print("No path found. Try a larger search radius or coordinates closer to walkable roads.")
        return

    coordinate_plot = visualize_data(path, node_lookup)

    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=13)
    folium.PolyLine(locations=coordinate_plot, color="blue", weight=5).add_to(m)

    print(path)
    m.save("index.html")


if __name__ == "__main__":
    main()
