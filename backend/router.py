from fastapi import APIRouter
from database import redis_client

router = APIRouter()

@router.get("/proxies/all")
def get_all_proxies():
    """
    Get all proxies for all levels.
    """
    return redis_client.get_all_proxies()

@router.get("/proxies/{level}")
def get_proxies(level: str):
    """
    Get proxies for a specific level.
    Levels: gold, silver, bronze
    """
    if level not in ["gold", "silver", "bronze"]:
        return {"error": "Invalid level"}
    
    return redis_client.get_proxies(level)

@router.get("/stats")
def get_stats():
    """
    Get counts of proxies in each level.
    """
    return redis_client.get_stats()

@router.post("/debug/inject")
def inject_test_data():
    """
    Manually inject a test proxy to verify the system.
    """
    print("DEBUG: Injecting test data via API...")
    redis_client.client.zadd("proxies:level1", {"TEST_PROXY:1234": 100})
    return {"message": "Injected TEST_PROXY:1234"}
