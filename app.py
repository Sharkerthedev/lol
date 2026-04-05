import os
from fastapi import FastAPI, Request, Response
import httpx
import uvicorn

app = FastAPI()

# 1. Cấu hình Discord Webhook (Sếp đã cung cấp)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1488126187007119431/ojbw6-JEM5Adz67SgGDAHyPX2SFWmZ6cVPfhT24MO9ItBNkurXi1xafTiVO0LMT65bg8"

# 2. Danh sách cổng Binance dự phòng
ENDPOINTS = [
    "https://api-gcp.binance.com",
    "https://api4.binance.com",
    "https://api3.binance.com",
    "https://api.binance.com"
]

# --- ROUTE TRANG CHỦ (Cho UptimeRobot & Health Check) ---
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "status": "online", 
        "message": "SaiGon Alpha Gateway is Active!",
        "features": ["Binance Proxy", "Discord Signal Forwarder"]
    }

# --- ROUTE GỬI TÍN HIỆU DISCORD (Dùng cho Sophia TA) ---
@app.post("/send-signal")
async def send_signal(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "⚠️ No content provided")
        
        # Tạo payload cho Discord
        payload = {
            "content": f"🚀 **[SAIGON ALPHA SIGNAL]**\n{message}",
            "username": "Sophia TA Assistant"
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10.0)
        
        return {"status": "success", "discord_code": resp.status_code}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

# --- ROUTE PROXY BINANCE (Dữ liệu nến/giá) ---
@app.get("/{path:path}")
async def proxy(path: str, request: Request):
    query_params = str(request.query_params)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.binance.com/"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for base in ENDPOINTS:
            target_url = f"{base}/{path}?{query_params}" if query_params else f"{base}/{path}"
            try:
                resp = await client.get(target_url, headers=headers, timeout=20.0)
                if resp.status_code not in [403, 451]:
                    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")
            except:
                continue
    
    return Response(content='{"error": "Binance Unreachable"}', status_code=502)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
