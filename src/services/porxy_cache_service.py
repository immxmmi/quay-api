import logging
import json
import os
from dotenv import load_dotenv
from api.client import ApiClient

logging.basicConfig(level=logging.INFO)

class ProxyCacheService:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("API_BASE_URL")
        self.token = os.getenv("API_TOKEN")

        if not self.base_url or not self.token:
            logging.error("Missing environment variables: API_BASE_URL or API_TOKEN")
            raise ValueError("Environment variables API_BASE_URL and API_TOKEN must be set")

        self.client = ApiClient(self.base_url, self.token)
        logging.info("ProxyCacheService initialized successfully")

    def create_proxy_cache(self, org_name: str, expiration_s: int = 86400, insecure: bool = False,
                           upstream_registry: str = "docker.io",
                           upstream_registry_username: str = None,
                           upstream_registry_password: str = None):
        """Creates a proxy cache configuration for the given organization."""
        logging.info(f"Creating proxy cache for organization '{org_name}'...")
        data = {
            "expiration_s": expiration_s,
            "insecure": insecure,
            "org_name": org_name,
            "upstream_registry": upstream_registry,
            "upstream_registry_username": upstream_registry_username,
            "upstream_registry_password": upstream_registry_password
        }
        try:
            response = self.client.post(f"organization/{org_name}/proxycache", data=json.dumps(data))
            logging.info(f"Proxy cache for organization '{org_name}' created successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to create proxy cache for '{org_name}': {e}")
            raise

    def get_proxy_cache(self, org_name: str):
        """Retrieves the proxy cache configuration for a specific organization."""
        logging.info(f"Fetching proxy cache for organization '{org_name}'...")
        try:
            response = self.client.get(f"organization/{org_name}/proxycache")
            logging.info(f"Proxy cache for '{org_name}' retrieved successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch proxy cache for '{org_name}': {e}")
            raise

    def delete_proxy_cache(self, org_name: str):
        """Deletes the proxy cache configuration for a specific organization."""
        logging.info(f"Deleting proxy cache for organization '{org_name}'...")
        try:
            response = self.client.delete(f"organization/{org_name}/proxycache")
            logging.info(f"Proxy cache for '{org_name}' deleted successfully.")
            return response
        except Exception as e:
            logging.error(f"Failed to delete proxy cache for '{org_name}': {e}")
            raise