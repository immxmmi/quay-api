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
        logging.info("Listing all organizations...")
        try:
            response = self.client.get("superuser/organizations/")
            logging.info("Organizations fetched successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to list organizations: {e}")
            raise

    def create_organization(self, name: str, email: str):
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
            error_message = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    api_error = e.response.json()
                    error_message = api_error.get("message", str(api_error))
                except Exception:
                    error_message = e.response.text

            # Prüfe auf bekannte, harmlose Fehler
            if "already exists" in error_message.lower() or "email has already been used" in error_message.lower():
                logging.error(f"Skipping creation: Organization '{name}' already exists or email in use.")
                return None

            logging.error(f"Failed to create organization '{name}': {error_message}")
            raise Exception(f"Failed to create organization '{name}': {error_message}")

    def get_organization(self, name: str):
        logging.info(f"Fetching organization '{name}' details...")
        try:
            response = self.client.get(f"organization/{name}")
            logging.info(f"Organization '{name}' details retrieved successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch organization '{name}': {e}")
            raise

    def delete_organization(self, name: str):
        logging.info(f"Deleting organization '{name}'...")
        try:
            response = self.client.delete(f"organization/{name}")
            logging.info(f"Organization '{name}' deleted successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to delete organization '{name}': {e}")
            raise

    def create_organizations_from_list(self, organizations: list[dict]):
        results = []
        for org in organizations:
            name = org.get("name")
            email = org.get("email")
            if not name or not email:
                logging.warning(f"Skipping invalid entry: {org}")
                continue

            try:
                logging.info(f"Creating organization '{name}'...")
                response = self.create_organization(name, email)
                logging.info(f"Organization '{name}' created successfully.")
                results.append({"name": name, "status": "created", "response": response})
            except Exception as e:
                logging.error(f"Error creating organization '{name}': {e}")
                results.append({"name": name, "status": "failed", "error": str(e)})
        logging.info("Bulk organization creation process completed.")
        return results