import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_database

router = APIRouter(prefix="", tags=["checkers"])


@router.get("/")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
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
