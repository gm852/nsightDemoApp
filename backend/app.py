from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base, User
from services import UserService
from models import UserResponse
from typing import List
import uvicorn
import time
import logging
import subprocess
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations with retry logic"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to run migrations (attempt {attempt + 1}/{max_retries})")
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd="/home/ubuntu/nsightTechnicalAssessment/backend",
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Database migrations completed successfully")
            logger.info(f"Migration output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to run migrations (attempt {attempt + 1}): {e}")
            logger.warning(f"Migration error: {e.stderr}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to run migrations after all retries")
                raise e
        except Exception as e:
            logger.warning(f"Failed to run migrations (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to run migrations after all retries")
                raise e
    
    return False

# Run migrations with retry logic
run_migrations()

app = FastAPI(
    title="User Profile API for Nsight Technical Assessment",
    description="API for fetching and caching user profile data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production you would, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/users/1", response_model=UserResponse)
async def get_user(
    bypass_cache: bool = Query(False, description="Force refetch from upstream API"),
    db: Session = Depends(get_db)
):
    """
    Get user data for user ID 1.
    Serves from cache if fresh (≤ 10 minutes old), otherwise fetches from upstream.
    """
    try:
        user_service = UserService(db)
        return user_service.get_user(1, bypass_cache=bypass_cache)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/users/refresh", response_model=UserResponse)
async def refresh_user(db: Session = Depends(get_db)):
    """
    Force refresh user data from upstream API and update cache.
    """
    try:
        user_service = UserService(db)
        return user_service.refresh_user(1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# more endpoints to show SQLAlchemy usage (:

@app.get("/api/users", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    """Get all users from the database using ORM"""
    try:
        user_service = UserService(db)
        users = user_service.get_all_users()
        return [
            UserResponse(
                name=user.name,
                username=user.username,
                email=user.email,
                website=user.website,
                companyName=user.company_name or ''
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/users/count")
async def get_user_count(db: Session = Depends(get_db)):
    """Get total number of users using ORM"""
    try:
        user_service = UserService(db)
        count = user_service.count_users()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/users/stale")
async def get_stale_users(db: Session = Depends(get_db)):
    """Get users with stale cache using ORM"""
    try:
        user_service = UserService(db)
        stale_users = user_service.get_stale_users()
        return {
            "stale_users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "username": user.username,
                    "updated_at": user.updated_at.isoformat()
                }
                for user in stale_users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID using ORM"""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            name=user.name,
            username=user.username,
            email=user.email,
            website=user.website,
            companyName=user.company_name or ''
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID using ORM"""
    try:
        user_service = UserService(db)
        success = user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User {user_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

