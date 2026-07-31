from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone



class InterviewRequest(BaseModel):
    job_role: str
    years_experience: int
    technical_keywords: list[str]
    company_type: str
    focus_area: str | None = None


class User(BaseModel):
    googleId: str
    name: str
    email: EmailStr
    profilePic: Optional[str] = ""
    totalAvlec: int = 0
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    profilePic: Optional[str] = ""
    totalAvlec: int = 0


class LoginRequest(BaseModel):
    code: str