from fastapi import APIRouter, status
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.get("/live", status_code=status.HTTP_200_OK)
def live():
    """Generic Kubernetes liveness probe — returns 200 if the app is running."""
    logging.info("Liveness probe checked: alive")
    return {"status": "alive"}

@router.get("/ready", status_code=status.HTTP_200_OK)
def ready():
    """Generic Kubernetes readiness probe — always ready."""
    logging.info("Readiness probe checked: ready")
    return {"status": "ready"}