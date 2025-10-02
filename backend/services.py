import httpx
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
from typing import Optional
from database import User
from models import UserResponse, UpstreamUserData
from config import UPSTREAM_API_URL, CACHE_DURATION_MINUTES

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def is_cache_stale(self, updated_at: datetime) -> bool:
        """Check if the cached data is stale (older than CACHE_DURATION_MINUTES)"""
        if not updated_at:
            return True
        
        now = datetime.now(timezone.utc)
        cache_duration = timedelta(minutes=CACHE_DURATION_MINUTES)
        return (now - updated_at) > cache_duration
    
    def fetch_from_upstream(self) -> UpstreamUserData:
        """Fetch user data from the upstream API"""
        with httpx.Client() as client:
            response = client.get(UPSTREAM_API_URL)
            response.raise_for_status()
            data = response.json()
            return UpstreamUserData(**data)
    
    def normalize_website(self, website: str) -> str:
        """Normalize website URL to include scheme (default https://)"""
        if not website:
            return ""
        
        if website.startswith(('http://', 'https://')):
            return website
        
        return f"https://{website}"
    
    def upsert_user(self, user_data: UpstreamUserData) -> User:
        """Insert or update user data in the database using SQLAlchemy ORM"""
        normalized_website = self.normalize_website(user_data.website)
        company_name = user_data.company.get('name', '') if user_data.company else ''
        current_time = datetime.now(timezone.utc)
        
        # Try to find existing user
        existing_user = self.db.query(User).filter(User.id == user_data.id).first()
        
        if existing_user:
            # Update existing user using ORM
            existing_user.name = user_data.name
            existing_user.username = user_data.username
            existing_user.email = user_data.email
            existing_user.website = normalized_website
            existing_user.company_name = company_name
            existing_user.updated_at = current_time
            
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        else:
            # Create new user using ORM
            new_user = User(
                id=user_data.id,
                name=user_data.name,
                username=user_data.username,
                email=user_data.email,
                website=normalized_website,
                company_name=company_name,
                updated_at=current_time
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
    
    def upsert_user_merge(self, user_data: UpstreamUserData) -> User:
        """Alternative upsert method using SQLAlchemy's merge() function"""
        normalized_website = self.normalize_website(user_data.website)
        company_name = user_data.company.get('name', '') if user_data.company else ''
        current_time = datetime.now(timezone.utc)
        
        # Create user object (existing or new)
        user = User(
            id=user_data.id,
            name=user_data.name,
            username=user_data.username,
            email=user_data.email,
            website=normalized_website,
            company_name=company_name,
            updated_at=current_time
        )
        
        # Use merge to handle both insert and update
        merged_user = self.db.merge(user)
        self.db.commit()
        self.db.refresh(merged_user)
        return merged_user
    
    def get_user(self, user_id: int, bypass_cache: bool = False) -> UserResponse:
        """Get user data, fetching from cache or upstream as needed"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # If no user in DB or cache is stale or bypass_cache is True
        if not user or self.is_cache_stale(user.updated_at) or bypass_cache:
            # Fetch from upstream and upsert
            upstream_data = self.fetch_from_upstream()
            user = self.upsert_user(upstream_data)
        
        return UserResponse(
            name=user.name,
            username=user.username,
            email=user.email,
            website=user.website,
            companyName=user.company_name or ''
        )
    
    def refresh_user(self, user_id: int) -> UserResponse:
        """Force refresh user data from upstream"""
        upstream_data = self.fetch_from_upstream()
        user = self.upsert_user(upstream_data)
        
        return UserResponse(
            name=user.name,
            username=user.username,
            email=user.email,
            website=user.website,
            companyName=user.company_name or ''
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID using ORM query"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username using ORM query"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_all_users(self) -> list[User]:
        """Get all users using ORM query"""
        return self.db.query(User).all()
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID using ORM"""
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def update_user_field(self, user_id: int, field: str, value: str) -> Optional[User]:
        """Update a specific field of a user using ORM"""
        user = self.get_user_by_id(user_id)
        if user and hasattr(user, field):
            setattr(user, field, value)
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
            return user
        return None
    
    def get_stale_users(self) -> list[User]:
        """Get all users with stale cache using ORM query"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=CACHE_DURATION_MINUTES)
        return self.db.query(User).filter(User.updated_at < cutoff_time).all()
    
    def count_users(self) -> int:
        """Count total users using ORM query"""
        return self.db.query(User).count()

