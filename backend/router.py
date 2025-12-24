from fastapi import APIRouter
from fastapi.responses import Response
from database import redis_client
import openpyxl
from io import BytesIO

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

@router.get("/proxies/export/excel")
def export_proxies_excel():
    """
    Export all proxies to an Excel file.
    """
    rows = redis_client.get_all_rows()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Proxies"
    
    # Headers
    headers = ["IP", "Port", "Country", "Country Code", "Latency (ms)", "Level", "Last Updated"]
    ws.append(headers)
    
    for row in rows:
        ws.append([
            row["ip"],
            row["port"],
            row["country"],
            row["country_code"],
            row["latency"],
            row["level"],
            row["last_updated"]
        ])
        
    # Save to buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="proxies.xlsx"'
    }
    
    return Response(content=buffer.getvalue(), headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@router.post("/debug/inject")
def inject_test_data():
    """
    Manually inject a test proxy to verify the system.
    """
    print("DEBUG: Injecting test data via API...")
    # This needs to be updated for SQLite if we want to keep it, but it's debug only.
    # redis_client.client.zadd("proxies:level1", {"TEST_PROXY:1234": 100})
    return {"message": "Debug injection disabled for SQLite migration"}
