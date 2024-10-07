import requests
import json
import time

# Input and output file paths
INPUT_FILE = './input_osm_ids.json'
OUTPUT_FILE = './output_osm_metadata.json'

# Nominatim API URL template
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/details.php?osmtype=R&osmid={osm_id}&class=boundary&addressdetails=1&hierarchy=0&group_hierarchy=1&format=json"

# Polygon and GeoJSON API URL templates
POLYGON_API_URL = "https://polygons.openstreetmap.fr/get_poly.py?id={osm_id}&params=0.020000-0.005000-0.005000"
GEOJSON_API_URL = "https://polygons.openstreetmap.fr/get_geojson.py?id={osm_id}&params=0.020000-0.005000-0.005000"

HTTP_HEADERS = {
    'Host': 'nominatim.openstreetmap.org',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://nominatim.openstreetmap.org/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'TE': 'trailers'
}

# Use a session to maintain cookies across requests
session = requests.Session()
session.headers.update(HTTP_HEADERS)

def fetch_nominatim_data(osm_id):
    """Fetch details from Nominatim API."""
    url = NOMINATIM_API_URL.format(osm_id=osm_id)
    response = requests.get(url, headers=HTTP_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch Nominatim data for OSM ID: {osm_id} {url} {response}")
        return None

def fetch_polygon_data(osm_id):
    """Fetch polygon (.poly) data."""
    url = POLYGON_API_URL.format(osm_id=osm_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch polygon data for OSM ID: {osm_id} {url} {response}")
        return None

def fetch_geojson_data(osm_id):
    """Fetch GeoJSON data."""
    url = GEOJSON_API_URL.format(osm_id=osm_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch GeoJSON data for OSM ID: {osm_id} {url} {response}")
        return None

def process_osm_ids(osm_data):
    """Process the OSM IDs and store the enriched data."""
    enriched_data = []
    
    for item in osm_data:
        item_data = {}

        osm_id = item['country']
        print(f"Processing OSM ID: {osm_id}")

        # Fetch Nominatim data
        nominatim_data = fetch_nominatim_data(osm_id)
        time.sleep(1)  # Sleep to respect API rate limits
        
        country_data = {
            "osm_id": osm_id,
            "nominatim_data": nominatim_data
        }

        provinces = item['provinces']
        
        # Process each province
        province_data = []
        for osm_id in provinces:
            print(f"Processing OSM ID: {osm_id}")

            # Fetch Nominatim data
            nominatim_data = fetch_nominatim_data(osm_id)
            time.sleep(1)  # Sleep to respect API rate limits
            
            # Fetch Polygon and GeoJSON data
            polygon_data = fetch_polygon_data(osm_id)
            time.sleep(1)
            geojson_data = fetch_geojson_data(osm_id)
            time.sleep(1)
            
            # Store the data for this province
            province_data.append({
                "osm_id": osm_id,
                "nominatim_data": nominatim_data,
                "polygon_data": polygon_data,
                "geojson_data": geojson_data
            })
        
        # Store the item data
        item_data['country'] = country_data
        item_data['provinces'] = province_data
        enriched_data.append(item_data)
    
    return enriched_data

def save_output_data(enriched_data):
    """Save the enriched data to the output JSON file."""
    with open(OUTPUT_FILE, 'w') as outfile:
        json.dump(enriched_data, outfile, indent=4)

def main():
    # Load the input JSON data
    with open(INPUT_FILE, 'r') as infile:
        osm_data = json.load(infile)
    
    # Process OSM IDs and fetch data
    enriched_data = process_osm_ids(osm_data)
    
    # Save the enriched data to output file
    save_output_data(enriched_data)
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
