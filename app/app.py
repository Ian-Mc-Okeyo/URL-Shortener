from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.short_url import router as shortener_router
from app.routes.redirect import router as redirect_router
from app.routes.analytics import router as analytics_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins -> can adjust once deployed or as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shortener_router)
app.include_router(redirect_router)
app.include_router(analytics_router)