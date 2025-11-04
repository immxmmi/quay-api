from fastapi import APIRouter, Response, status
import os
import logging
import requests

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.get("/live", status_code=status.HTTP_200_OK)
def live():
    """Generic Kubernetes liveness probe — returns 200 if the app is running."""
    return {"status": "alive"}

@router.get("/ready")
def ready(response: Response):
    """Generic Kubernetes readiness probe — checks env vars and optional API connectivity."""
    base_url = os.getenv("API_BASE_URL")
    token = os.getenv("API_TOKEN")

    if not base_url or not token:
        logging.warning("Readiness: Missing required environment variables (API_BASE_URL or API_TOKEN).")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready", "reason": "missing environment variables"}

    try:
        logging.info(f"Readiness: Checking connectivity to {base_url} ...")
        resp = requests.get(base_url, headers={"Authorization": f"Bearer {token}"}, timeout=3)
        if resp.ok:
            logging.info("Readiness: External API reachable.")
            return {"status": "ready"}
        else:
            logging.error(f"Readiness: API returned status code {resp.status_code}.")
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "not ready", "reason": f"API returned {resp.status_code}"}
    except requests.RequestException as e:
        logging.error(f"Readiness: Could not reach API_BASE_URL — {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready", "reason": "API unreachable"}