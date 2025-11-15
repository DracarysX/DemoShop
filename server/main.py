"""
FastAPI Coupon Server - Refactored
Run with: uvicorn main:app --reload --port 8080
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

# Initialize FastAPI app
app = FastAPI(title="DemoShop Coupon API")

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Enable CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes after app initialization to avoid circular imports
from routes import coupon, analytics, similarity

# Register routes
app.include_router(coupon.router)
app.include_router(analytics.router)
app.include_router(similarity.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main analytics dashboard index"""
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html"), "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

