import os
from fastapi import FastAPI, Request, Response
import httpx
import uvicorn

app = FastAPI()

# Danh sách cổng Binance ưu tiên cổng Google Cloud và api4 (thoáng nhất)
ENDPOINTS = [
    "https://api-gcp.binance.com",
    "https://api4.binance.com",
    "https://api3.binance.com",
    "https://api1.binance.com",
    "https://api.binance.com"
]

@app.get("/")
async def root():
    return {"status": "online", "message": "SaiGon Alpha Proxy is running on Singapore Server!"}

@app.get("/{path:path}")
async def proxy(path: str, request: Request):
    query_params = str(request.query_params)
    
    # Giả lập Header trình duyệt để Binance không nghi ngờ
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.binance.com/",
        "Origin": "https://www.binance.com"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for base in ENDPOINTS:
            target_url = f"{base}/{path}?{query_params}" if query_params else f"{base}/{path}"
            try:
                # Thử gọi Binance
                resp = await client.get(target_url, headers=headers, timeout=15.0)
                
                # Nếu không bị 451 hoặc 403, trả kết quả về ngay
                if resp.status_code not in [403, 451]:
                    return Response(
                        content=resp.content,
                        status_code=resp.status_code,
                        media_type="application/json"
                    )
            except Exception:
                continue
    
    return Response(content='{"error": "All Binance endpoints are restricted from this IP."}', status_code=451)

if __name__ == "__main__":
    # Render cấp cổng qua biến môi trường PORT, nếu không có mặc định là 10000
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
