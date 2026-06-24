import pytest
from jsonschema import validate

# 1. Lifecycle Fixture: Creates a booking before a test and deletes it after
@pytest.fixture
def created_booking(client):
    payload = {
        "firstname": "Jim", "lastname": "Brown", "totalprice": 111, 
        "depositpaid": True, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}
    }
    response = client.create_booking(payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]
    
    yield booking_id  # Provide the ID to the test
    
    client.delete_booking(booking_id)

# 2. Updated GET test using the dynamic fixture
def test_get_created_booking(client, created_booking, booking_schema):
    response = client.get_booking(created_booking)
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 2.0
    validate(instance=response.json(), schema=booking_schema)

# 3. Dedicated Negative Test for invalid ID
def test_get_invalid_booking(client):
    response = client.get_booking(9999999)
    assert response.status_code == 404

# 4. Updated Create Booking test
@pytest.mark.parametrize("payload, expected_status", [
    ({"firstname": "Jim", "lastname": "Brown", "totalprice": 111, "depositpaid": True, 
      "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}}, 200),
    ({"firstname": "Bad", "lastname": "Data"}, 500) 
],ids=["valid-payload", "invalid-payload"])
def test_create_booking(client, payload, expected_status):
    response = client.create_booking(payload)
    assert response.status_code == expected_status

    #5.Delete the booking id 

def test_update_booking(client, created_booking):
    new_payload = {
        "firstname": "James", "lastname": "Brown", "totalprice": 333, 
        "depositpaid": True, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}
    }
    response = client.update_booking(created_booking, new_payload)
    assert response.status_code == 200
    assert response.json()["firstname"] == "James"