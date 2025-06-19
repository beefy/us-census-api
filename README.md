# us-census-api
Get population data for a coordinate and radius

## Environment Setup

```
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Started

To generate a US Census API key:

 - Visit the US Census Bureau Request a Key page: https://api.census.gov/data/key_signup.html
 - Fill out the form with your name, email, and organization (optional).
 - Submit the form.
 - Check your email for your API key and follow any instructions provided.

Store the api key as an environment variable

```
export CENSUS_API_KEY=your_api_key_here
```

## Run the script

```
python3.11 main.py
```
