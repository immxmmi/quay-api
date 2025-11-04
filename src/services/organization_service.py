import logging

logging.basicConfig(level=logging.INFO)

from api.client import ApiClient
from dotenv import load_dotenv
import os
import json

class OrganizationService:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("API_BASE_URL")
        self.token = os.getenv("API_TOKEN")

        if not self.base_url or not self.token:
            logging.error("Missing environment variables: API_BASE_URL or API_TOKEN")
            raise ValueError("Environment variables API_BASE_URL and API_TOKEN must be set")

        self.client = ApiClient(self.base_url, self.token)
        logging.info("OrganizationService initialized successfully")

    def list_organizations(self):
        """Fetches all organizations."""
        logging.info("Listing all organizations...")
        try:
            response = self.client.get("superuser/organizations/")
            logging.info("Organizations fetched successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to list organizations: {e}")
            raise

    def create_organization(self, name: str, email: str):
        """Creates a new organization with the given name and email."""
        logging.info(f"Creating organization '{name}' with email '{email}'...")
        data = {
            "name": name,
            "email": email
        }
        try:
            response = self.client.post("organization/", data=json.dumps(data))
            logging.info(f"Organization '{name}' created successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to create organization '{name}': {e}")
            raise

    def get_organization(self, name: str):
        """Fetches details of a specific organization by name."""
        logging.info(f"Fetching organization '{name}' details...")
        try:
            response = self.client.get(f"organization/{name}")
            logging.info(f"Organization '{name}' details retrieved successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch organization '{name}': {e}")
            raise

    def delete_organization(self, name: str):
        """Deletes an organization by name."""
        logging.info(f"Deleting organization '{name}'...")
        try:
            response = self.client.delete(f"organization/{name}")
            logging.info(f"Organization '{name}' deleted successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to delete organization '{name}': {e}")
            raise