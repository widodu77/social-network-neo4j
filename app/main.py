"""
FastAPI main application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import get_neo4j_driver, close_neo4j_driver
from app.routers import users, recommendations, paths, health, llm

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    driver = get_neo4j_driver()
    driver.verify_connectivity()
    print("Connected to Neo4j database")

    yield

    # Shutdown
    close_neo4j_driver()
    print("Closed Neo4j database connection")


# Create FastAPI application
app = FastAPI(
    title="Social Network Recommendation System",
    description="A LinkedIn-style professional network with friend and job recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(paths.router, prefix="/api", tags=["Paths"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM-Powered Queries"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Social Network Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
