import requests
import os

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


def run():
    api_key = os.getenv('CENSUS_API_KEY')

    # Get census block FIPS code for the given lat/lon
    block_fips = get_census_block_fips(COORDINATE_LATITUDE, COORDINATE_LONGITUDE)
    state_fips = block_fips[:2]
    county_fips = block_fips[2:5]
    tract_code = block_fips[5:11]
    block_code = block_fips[11:]

    # Get population for the census block
    population_response = call_us_census_api(
        'https://api.census.gov/data/2020/dec/pl',
        {
            'get': 'P1_001N',  # Total population
            'for': f'block:{block_code}',
            'in': f'state:{state_fips} county:{county_fips} tract:{tract_code}'
        },
        api_key
    )
    print('Population for census block:', population_response)

    # Parse the population response
    population_data = population_response[1][0]
    print('Population:', population_data)


if __name__ == "__main__":
    run()
