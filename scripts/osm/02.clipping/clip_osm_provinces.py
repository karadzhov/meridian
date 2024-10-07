import json
import os
import subprocess
import requests

# Input JSON file and URLs
INPUT_METADATA_JSON = "input_osm_metadata.json"
INPUT_URLS_JSON = "input_osm_urls.json"

# Download OSM PBF if not present
def download_pbf(pbf_file, pbf_url):
    if not os.path.exists(pbf_file):
        print(f"Downloading {pbf_file} OSM PBF file...")
        response = requests.get(pbf_url, stream=True)
        if response.status_code == 200:
            with open(pbf_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"{pbf_file} OSM PBF file downloaded.")
        else:
            raise Exception(f"Failed to download {pbf_file} OSM PBF file. Status code: {response.status_code}")
    else:
        print(f"{pbf_file} OSM PBF file already exists.")

# Use Osmosis to clip each province from the PBF file
def clip_province(pbf_file, province_data, polygon_data, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the province name (use 'name:en' if available, otherwise fallback to 'osm_id')
    province_name = province_data.get('nominatim_data', {}).get('names', {}).get('name:en', f"province_{province_data['osm_id']}")
    province_name = province_name.replace(" ", "_").lower()  # Clean the name for a valid filename

    # Write polygon data to a temporary poly file
    poly_filename = f"{province_name}.poly"
    with open(poly_filename, 'w') as poly_file:
        poly_file.write(polygon_data)
    
    # Use Osmosis to cut the province based on the poly file
    output_file = os.path.join(output_dir, f"{province_name}-latest.osm.pbf")
    print(f"Clipping {province_name} to {output_file}...")
    
    osmosis_command = [
        "osmosis",
        "--read-pbf", f"file={pbf_file}",
        "--bp", "clipIncompleteEntities=true", f"file={poly_filename}",
        "--write-pbf", "granularity=10000", f"file={output_file}"
    ]
    
    # Run the Osmosis command
    try:
        subprocess.run(osmosis_command, check=True)
        print(f"Province {province_name} clipped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while clipping province {province_name}: {e}")
    
    # Clean up the temporary poly file
    os.remove(poly_filename)

def main():
    # Load the input metadata JSON file
    with open(INPUT_METADATA_JSON, 'r') as f:
        osm_metadata = json.load(f)

    with open(INPUT_URLS_JSON, 'r') as f:
        osm_urls = json.load(f)

    # Clip each province using Osmosis    
    for item_data in osm_metadata:
        country = item_data['country']
        osm_id = country['osm_id']
        country_name = country.get('nominatim_data', {}).get('names', {}).get('name:en', f"country_{osm_id}").lower()
        output_dir = "output"
        pbf_file = f"{output_dir}/{country_name}-latest.osm.pbf"
        url = osm_urls[f"{osm_id}"]

        download_pbf(pbf_file, url)

        for province in item_data['provinces']:
            province_polygon = province.get('polygon_data')
            province_output_dir = f"{output_dir}/{country_name}"
            if province_polygon:
                clip_province(pbf_file, province, province_polygon, province_output_dir)
            else:
                print(f"No polygon data available for province OSM ID {province['osm_id']}")

if __name__ == "__main__":
    main()
