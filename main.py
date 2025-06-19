import requests
import os


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


def run():
    api_key = os.getenv('CENSUS_API_KEY')
    print(call_us_census_api(
        'https://api.census.gov/data/2020/dec/pl',
        {'get': 'NAME', 'for': 'state:*'},
        api_key
    ))


if __name__ == "__main__":
    run()
