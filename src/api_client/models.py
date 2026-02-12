from typing import Optional

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


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
