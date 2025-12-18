"""
Health check endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.database import get_neo4j_driver

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifies API and database connectivity.
    """
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()

        # Test database query
        with driver.session() as session:
            result = session.run("RETURN 1 AS health")
            health_status = result.single()["health"]

        return {
            "status": "healthy",
            "database": "connected",
            "health_check": health_status == 1,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}") from e
