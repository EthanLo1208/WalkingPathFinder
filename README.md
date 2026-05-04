# WalkingPathFinder
A* algorithm on real geographic map data to find the optimal walking route between two locations.


## Demo

1)Enter geographic coordinates. The following example starts from Longshan Temple and ends at Jiufen Old Street.
<img width="422" height="30" alt="Screenshot 2026-05-04 at 9 45 15 PM" src="https://github.com/user-attachments/assets/107ee8a6-e04a-4fce-80e5-0d5e84a440c8" />

2)After a few seconds, an index.html file should be downloaded. The file contains an interactive map that highlights the optimal route in blue.
<img width="664" height="525" alt="Screenshot 2026-05-04 at 9 50 36 PM" src="https://github.com/user-attachments/assets/25f0c07c-24c0-45d7-ae65-7570ebaa6f86" />

*The algorithom purposely avoids highways as they are not walkable.





## How It Works
1. Takes two geographic coordinates as input
2. Fetches real path/node data from OpenStreetMap through Overpass API
3. Builds a graph of walkable nodes and edges with the Haversine formula
4. Runs A* algorithom to compute the shortest walking route
5. Visualize the result on an interactive map through Folium

## Usage
'''bash
pip install -r requirements.txt
python Astar.py
'''
Enter coordinates when prompted. Note that the program expects coordinates following decimal degrees.

An `index.html` file will be generated. Open it in your browser to see the route.

## Dependencies
- `requests`: fetching OpenStreetMap data
- `folium`: map visualization
- Standard library: `heapq`, `math`, `collections`

## Limitations
- Works best for points within a few kilometers of each other
- Requires an internet connection to fetch map data
- Dense urban areas may take longer to query

