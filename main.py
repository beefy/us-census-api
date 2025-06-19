import requests
import os
import math

COORDINATE_LATITUDE = 43.528484
COORDINATE_LONGITUDE = -116.147614
RADIUS = 2.03  # in miles


def call_us_census_api(endpoint: str, params: dict, api_key: str = None):
    """
    Calls the US Census API with the given endpoint and parameters.
    Args:
        endpoint (str): The API endpoint URL (e.g.,
            'https://api.census.gov/data/2020/dec/pl').
        params (dict): Dictionary of query parameters (e.g.,
            {'get': 'NAME', 'for': 'state:*'}).
        api_key (str, optional): Your Census API key. If provided,
            it will be added to params.
    Returns:
        dict or list: The JSON response from the API.
    Raises:
        requests.HTTPError: If the request fails.
    """
    if api_key:
        params['key'] = api_key

    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()


def get_census_block_fips(lat: float, lon: float):
    """
    Get the census block FIPS code for the given latitude and longitude.
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
    Returns:
        str: The census block FIPS code.
    """
    fcc_url = 'https://geo.fcc.gov/api/census/block/find'
    fcc_params = {
        'latitude': lat,
        'longitude': lon,
        'format': 'json'
    }
    fcc_response = requests.get(fcc_url, params=fcc_params)
    fcc_response.raise_for_status()
    fcc_data = fcc_response.json()
    return fcc_data['Block']['FIPS']


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth
    (in miles).
    """
    R = 3958.8  # Earth radius in miles
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) *
         math.sin(dlambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def generate_points_within_radius(center_lat, center_lon, radius, step=0.01):
    """
    Generate a grid of lat/lon points within a radius (in miles) of the center.
    step: grid step in degrees (smaller = more accurate, slower)
    """
    points = []
    lat_range = radius / 69.0  # 1 deg latitude ~ 69 miles
    lon_range = radius / (math.cos(math.radians(center_lat)) * 69.0)
    lat_min = center_lat - lat_range
    lat_max = center_lat + lat_range
    lon_min = center_lon - lon_range
    lon_max = center_lon + lon_range
    lat = lat_min
    while lat <= lat_max:
        lon = lon_min
        while lon <= lon_max:
            if haversine_distance(center_lat, center_lon, lat, lon) <= radius:
                points.append((lat, lon))

            lon += step

        lat += step

    return points


def get_unique_blocks_within_radius(center_lat, center_lon, radius):
    """
    Get unique census block FIPS codes within the radius of the center point.
    """
    points = generate_points_within_radius(center_lat, center_lon, radius)
    block_fips_set = set()
    for lat, lon in points:
        fips = get_census_block_fips(lat, lon)
        block_fips_set.add(fips)

    return list(block_fips_set)


def get_population_for_block_fips(block_fips, api_key=None):
    state_fips = block_fips[:2]
    county_fips = block_fips[2:5]
    tract_code = block_fips[5:11]
    block_code = block_fips[11:]
    population_response = call_us_census_api(
        'https://api.census.gov/data/2020/dec/pl',
        {
            'get': 'P1_001N',
            'for': f'block:{block_code}',
            'in': f'state:{state_fips} county:{county_fips} tract:{tract_code}'
        },
        api_key
    )

    return int(population_response[1][0])


def run():
    api_key = os.getenv('CENSUS_API_KEY')

    # Get all unique census blocks within the radius
    block_fips_list = get_unique_blocks_within_radius(
        COORDINATE_LATITUDE,
        COORDINATE_LONGITUDE,
        RADIUS
    )

    print(f'Found {len(block_fips_list)} unique blocks within {RADIUS} miles')

    # Get and sum population for each block
    total_population = 0
    for block_fips in block_fips_list:
        pop = get_population_for_block_fips(block_fips, api_key)
        total_population += pop

    print(f'Total population within {RADIUS} miles: {total_population}')


if __name__ == "__main__":
    run()
