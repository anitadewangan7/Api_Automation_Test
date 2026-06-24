import requests
import os
import logging
from dotenv import load_dotenv

# Configure logging to output to console and potentially a file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class BookerClient:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.auth = (os.getenv("USERNAME"), os.getenv("PASSWORD"))
        self.token = self._get_token()

    def _get_token(self):
        url = f"{self.base_url}/auth"
        response = requests.post(url, json={"username": self.auth[0], "password": self.auth[1]})
        logger.info(f"Auth Request: {url} | Status: {response.status_code}")
        return response.json().get("token")

    def get_booking(self, booking_id):
        url = f"{self.base_url}/booking/{booking_id}"
        response = requests.get(url)
        logger.info(f"GET Request: {url} | Status: {response.status_code}")
        return response

    
    def create_booking(self, payload):
        url = f"{self.base_url}/booking"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"POST Request: {url} | Status: {response.status_code} | Body: {response.text}")
        return response
    
    def delete_booking(self, booking_id):
        url = f"{self.base_url}/booking/{booking_id}"
        # The API requires the token for DELETE requests
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"token={self.token}"
        }
        response = requests.delete(url, headers=headers)
        logger.info(f"DELETE Request: {url} | Status: {response.status_code}")
        return response
    
    def update_booking(self, booking_id, payload):
        url = f"{self.base_url}/booking/{booking_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f"token={self.token}"
        }
        response = requests.put(url, json=payload, headers=headers)
        return response
    
