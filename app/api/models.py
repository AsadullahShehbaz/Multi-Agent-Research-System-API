"""
API Models - Pydantic request/response models
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "strongpassword123"
            }
        }


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    username: str
    email: str


class UserResponse(BaseModel):
    """User information response"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: str


class ResearchRequest(BaseModel):
    """Research request"""
    query: str = Field(..., min_length=5, description="Research question")
    max_iterations: Optional[int] = Field(2, ge=1, le=5)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Latest AI developments at End of 2025",
                "max_iterations": 2
            }
        }


class ResearchResponse(BaseModel):
    """Research response"""
    id: int
    query: str
    final_report: str
    status: str
    processing_time: Optional[int]
    iterations: Optional[int] = None
    created_at: str


class ResearchHistoryItem(BaseModel):
    """Research history item"""
    id: int
    query: str
    status: str
    created_at: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str

