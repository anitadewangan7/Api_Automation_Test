import pytest
import json
import logging 
from src.api_client import BookerClient

@pytest.fixture(scope="session")
def client():
    return BookerClient()

@pytest.fixture(scope="session")
def booking_schema():
    with open("src/schemas/booking_schema.json") as f:
        return json.load(f)

def pytest_metadata(metadata):
    metadata['API Project'] = 'RESTful Booker'
    metadata['Environment'] = 'Production'
    metadata.pop("Packages", None) 

