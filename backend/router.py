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

@router.get("/api/history")
def get_history():
    """
    Get historical proxy counts for the graph.
    """
    return redis_client.get_history()

@router.get("/api/proxies/external")
def get_external_proxies():
    """
    Get a plain text list of all proxies (IP:Port) for external use.
    """
    all_proxies = redis_client.get_all_proxies()
    proxy_list = []
    
    for level in ["gold", "silver", "bronze"]:
        for p in all_proxies[level]:
            # p["proxy"] is "IP:PORT:COUNTRY:CODE"
            # We just want IP:PORT
            parts = p["proxy"].split(":")
            if len(parts) >= 2:
                proxy_list.append(f"{parts[0]}:{parts[1]}")
                
    return Response(content="\n".join(proxy_list), media_type="text/plain")
