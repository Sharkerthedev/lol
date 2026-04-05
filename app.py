import os
from fastapi import FastAPI, Request, Response
import httpx
import uvicorn

app = FastAPI()

# Danh sách cổng Binance ưu tiên cổng Google Cloud và api4 (ít bị chặn nhất)
ENDPOINTS = [
    "https://api-gcp.binance.com",
    "https://api4.binance.com",
    "https://api3.binance.com",
    "https://api1.binance.com",
    "https://api.binance.com"
]

# Route trang chủ: Hỗ trợ cả GET và HEAD để UptimeRobot không báo lỗi 405
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "status": "online", 
        "message": "SaiGon Alpha Proxy is active on Singapore Server!",
        "note": "Ready for Sophia TA analysis"
    }

# Route Proxy: Nhận mọi yêu cầu API và chuyển tiếp sang Binance
@app.get("/{path:path}")
async def proxy(path: str, request: Request):
    query_params = str(request.query_params)
    
    # Giả lập Header trình duyệt xịn để tránh bị Binance soi
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.binance.com/",
        "Origin": "https://www.binance.com"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for base in ENDPOINTS:
            # Ghép URL: Nếu có tham số (query) thì thêm vào, không thì thôi
            target_url = f"{base}/{path}?{query_params}" if query_params else f"{base}/{path}"
            try:
                # Thực hiện gọi lệnh sang Binance
                resp = await client.get(target_url, headers=headers, timeout=20.0)
                
                # Nếu không bị chặn địa lý (451) hoặc cấm (403), trả kết quả về ngay
                if resp.status_code not in [403, 451]:
                    return Response(
                        content=resp.content,
                        status_code=resp.status_code,
                        media_type="application/json"
                    )
            except Exception:
                # Nếu cổng này lỗi, tự động nhảy sang cổng tiếp theo trong danh sách
                continue
    
    # Nếu thử hết tất cả các cổng mà vẫn tịt
    return Response(
        content='{"error": "Binance is temporarily unreachable from this IP. Please wait a few minutes."}', 
        status_code=502
    )

if __name__ == "__main__":
    # Render cấp cổng (Port) qua biến môi trường, mặc định là 10000 nếu chạy local
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
