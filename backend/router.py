from fastapi import APIRouter, Depends, HTTPException, status
from database import redis_client
from pydantic import BaseModel
import openpyxl
from fastapi.responses import FileResponse, Response
import os
from io import BytesIO

router = APIRouter()

# Pydantic models
class UserUpgrade(BaseModel):
    email: str
    new_limit: int

# Dependency to get current user is injected in main.py via app.include_router

@router.get("/proxies/all")
async def get_all_proxies(current_user: dict = Depends()): # current_user injected by main
    # Use the user's proxy limit
    limit = current_user["proxy_limit"]
    email = current_user["email"]
    is_admin = current_user["is_admin"]
    
    # Ensure proxies are assigned
    if not is_admin:
        redis_client.assign_proxies(email, limit)
    
    return redis_client.get_all_proxies(limit=limit if not is_admin else None, user_email=email, is_admin=is_admin)

@router.get("/proxies/{level}")
async def get_proxies_by_level(level: str, current_user: dict = Depends()):
    if level not in ["gold", "silver", "bronze"]:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    limit = current_user["proxy_limit"]
    email = current_user["email"]
    is_admin = current_user["is_admin"]
    
    if not is_admin:
        redis_client.assign_proxies(email, limit)
        
    return redis_client.get_proxies(level, limit=limit if not is_admin else None, user_email=email, is_admin=is_admin)

@router.get("/stats")
async def get_stats():
    return redis_client.get_stats()

@router.get("/proxies/export/excel")
async def export_excel(current_user: dict = Depends()):
    # Export respects limit too
    limit = current_user["proxy_limit"]
    data = redis_client.get_all_proxies(limit=limit)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Proxies"
    
    # Headers
    headers = ["IP", "Port", "Country", "Country Code", "Latency (ms)", "Level"]
    ws.append(headers)
    
    for level in ["gold", "silver", "bronze"]:
        for p in data[level]:
            # p["proxy"] is "IP:PORT:COUNTRY:CODE"
            parts = p["proxy"].split(":")
            ip = parts[0]
            port = parts[1] if len(parts) > 1 else ""
            country = parts[2] if len(parts) > 2 else "Unknown"
            country_code = parts[3] if len(parts) > 3 else ""
            
            ws.append([
                ip,
                port,
                country,
                country_code,
                p["latency"],
                level
            ])

    # Save to buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="proxies.xlsx"'
    }
    
    return Response(content=buffer.getvalue(), headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Admin Endpoint
@router.post("/admin/upgrade")
async def upgrade_user(upgrade_data: UserUpgrade, current_user: dict = Depends()):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    redis_client.update_user_limit(upgrade_data.email, upgrade_data.new_limit)
    return {"message": f"User {upgrade_data.email} upgraded to {upgrade_data.new_limit} proxies"}

# Public/External API (Protected by token still, but maybe different rate limits later)
@router.get("/api/proxies/external")
async def get_external_proxies(limit: int = 10, current_user: dict = Depends()):
    # Ensure they don't exceed their assigned limit
    user_limit = current_user["proxy_limit"]
    actual_limit = min(limit, user_limit)
    
    all_data = redis_client.get_all_proxies(limit=actual_limit)
    # Flatten the list
    flat_list = []
    for level in all_data:
        for p in all_data[level]:
             # p["proxy"] is "IP:PORT:COUNTRY:CODE"
             # We just want IP:PORT
            parts = p["proxy"].split(":")
            if len(parts) >= 2:
                flat_list.append(f"{parts[0]}:{parts[1]}")
        
    return Response(content="\n".join(flat_list[:actual_limit]), media_type="text/plain")

@router.get("/api/history")
async def get_history():
    return redis_client.get_history()
