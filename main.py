from fastapi import FastAPI, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timezone
from typing import Optional

#main app here
app = FastAPI()

# Permits the CORS headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "name is not a string"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Upstream or server failure"}
    )

# Classify name endpoint
@app.get("/api/classify")
async def classify_name(name: Optional[str] = Query(None)):
    if name is None or name.strip() == "":
        # Returns 400 if name is missing or empty
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing or empty name parameter"}
        )
    
    # Check if name is essentially a number
    try:
        float(name)
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "name is not a string"}
        )
    except ValueError:
        pass
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.genderize.io/?name={name}", timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            gender = data.get("gender")
            probability = data.get("probability", 0.0)
            sample_size = data.get("count", 0)
            
            if gender is None or sample_size == 0:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "No prediction available for the provided name"}
                )
            
            is_confident = bool((probability >= 0.7) and (sample_size >= 100))
            
            processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            return {
                "status": "success",
                "data": {
                    "name": name,
                    "gender": gender,
                    "probability": probability,
                    "sample_size": sample_size,
                    "is_confident": is_confident,
                    "processed_at": processed_at
                }
            }
            
    except httpx.HTTPStatusError as exc:
        # If genderize API returns an error
        status_code = exc.response.status_code if exc.response.status_code in [500, 502] else 502
        return JSONResponse(
            status_code=status_code,
            content={"status": "error", "message": "Upstream or server failure"}
        )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=502,
            content={"status": "error", "message": "Upstream or server failure"}
        )

# Root endpoint for basic health check
@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to Wisdom Ehirim Genderize API. Access /api/classify?name={name}"}
