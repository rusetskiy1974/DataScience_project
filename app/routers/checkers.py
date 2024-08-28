import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_database

router = APIRouter(prefix="", tags=["checkers"])


@router.get("/")
def health_check():
    """Health check endpoint.

    This endpoint provides a simple status check for the application. It returns a status code of 200 and a message indicating that the application is working.

    Returns:
        dict: A dictionary with the following keys:
            - `status_code` (int): The HTTP status code (200).
            - `detail` (str): A message indicating the status ("ok").
            - `result` (str): A message indicating the application is working ("working").
    """
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    """Database health check endpoint.

    This endpoint checks the connectivity to the database by executing a simple SQL query. It returns a message if the database is properly configured and connected.

    Args:
        db (AsyncSession): Dependency for the asynchronous database session.

    Returns:
        dict: A dictionary with the following key:
            - `message` (str): A welcome message if the database connection is successful.

    Raises:
        HTTPException: If there is an error connecting to the database or if the database is not configured correctly. The status code is 500.
    """
    try:
        result = await db.execute(select(1))
        row = result.fetchone()
        if row is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI"}
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")
