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
    """Generic Kubernetes readiness probe — checks env vars only."""
    base_url = os.getenv("API_BASE_URL")
    token = os.getenv("API_TOKEN")

    if not base_url or not token:
        logging.warning("Readiness: Missing required environment variables (API_BASE_URL or API_TOKEN).")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready", "reason": "missing environment variables"}

    return {"status": "ready"}

@router.get("/dependency")
def dependency(response: Response):
    """Checks connectivity to the external API defined by API_BASE_URL and API_TOKEN."""
    base_url = os.getenv("API_BASE_URL")
    token = os.getenv("API_TOKEN")

    if not base_url or not token:
        logging.warning("Dependency check: Missing required environment variables (API_BASE_URL or API_TOKEN).")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "reason": "missing environment variables"}

    try:
        logging.info(f"Dependency check: Checking connectivity to {base_url} ...")
        resp = requests.get(base_url, headers={"Authorization": f"Bearer {token}"}, timeout=3)
        if resp.ok:
            logging.info("Dependency check: External API reachable.")
            return {"status": "ok"}
        else:
            logging.error(f"Dependency check: API returned status code {resp.status_code}.")
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "error", "reason": f"API returned {resp.status_code}"}
    except requests.RequestException as e:
        logging.error(f"Dependency check: Could not reach API_BASE_URL — {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "reason": "API unreachable"}