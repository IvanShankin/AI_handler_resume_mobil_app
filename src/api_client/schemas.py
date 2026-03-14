from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr

class ProcessingStatus(Enum):
    IN_PROGRESS = "in_progress"
    SUCCESSFULLY = "successfully"
    FAILED = "failed"


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
    requirement_id: int
    user_id: int
    requirements: str


class DeleteProcessingResponse(BaseModel):
    processing_ids: List[int]


class DeleteResumeResponse(DeleteProcessingResponse):
    resume_ids: List[int]


class DeleteRequirementsResponse(DeleteResumeResponse):
    requirement_ids: List[int]


class ResumeOut(BaseModel):
    resume_id: int
    user_id: int
    resume: str


class ProcessingOut(BaseModel):
    processing_id: int
    resume_id: int
    requirement_id: int
    user_id: int

    status: ProcessingStatus
    success: bool = False

    message_error: str | None = None
    wait_seconds: str | None = None

    score: int | None = None
    matches: List[str] | None = None
    verdict: str | None = None
    recommendation: str | None = None

    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
