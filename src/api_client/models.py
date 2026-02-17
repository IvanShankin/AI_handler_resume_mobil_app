from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    user_id: int
    username: EmailStr
    full_name: Optional[str]
    created_at: str


class RequirementsOut(BaseModel):
    requirements_id: int
    user_id: int
    requirements: str


class IsDeleteOut(BaseModel):
    is_deleted: bool


class ResumeOut(BaseModel):
    resume_id: int
    user_id: int
    resume: str


class ProcessingDetailOut(BaseModel):
    processing_id: int
    resume_id: int
    requirements_id: int
    user_id: int

    success: bool
    message_error: str # только при success == False
    wait_seconds: int # только при success == False

    score: int
    verdict: str
    resume: str
    requirements: str
    matches: List[str]
    recommendation: str
    create_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
