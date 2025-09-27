from pydantic import BaseModel, EmailStr, validator
from datetime import date, time
from typing import Optional, List, Dict
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "student"
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        # Truncate password to 72 bytes for bcrypt compatibility
        v = v[:72] if len(v.encode('utf-8')) > 72 else v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str = "student"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None

class TokenData(BaseModel):
    email: Optional[str] = None

# Assessment Schemas
class AssessmentResponse(BaseModel):
    question_id: int
    score: int  # 0-3 scale

class AssessmentSubmit(BaseModel):
    assessment_type: str  # PHQ-9, GAD-7
    responses: List[AssessmentResponse]

class AssessmentResultResponse(BaseModel):
    id: int
    assessment_type: str
    total_score: int
    severity_level: str
    recommendations: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AssessmentHistoryResponse(BaseModel):
    assessments: List[AssessmentResultResponse]
    total_count: int

# Forum Schemas
class ForumCategoryCreate(BaseModel):
    name: str
    description: str
    color: str = "#6c8ef5"
    icon: str = "fas fa-comments"

class ForumCategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    color: str
    icon: str
    post_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ForumPostCreate(BaseModel):
    title: str
    content: str
    category_id: int

class ForumPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None

class ForumPostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    category_id: int
    is_pinned: bool
    is_locked: bool
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ForumCommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class ForumCommentUpdate(BaseModel):
    content: str

class ForumCommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    parent_id: Optional[int]
    like_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ForumPostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    category_id: int
    is_pinned: bool
    is_locked: bool
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    comments: List[ForumCommentResponse]
    
    class Config:
        from_attributes = True

class ForumPostListResponse(BaseModel):
    posts: List[ForumPostResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Appointment Schemas
class AppointmentSlotCreate(BaseModel):
    counselor_name: str
    counselor_email: str
    date: date
    start_time: time
    end_time: time

class AppointmentSlotResponse(BaseModel):
    id: int
    counselor_name: str
    counselor_email: str
    date: date
    start_time: time
    end_time: time
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    slot_id: int
    concern_type: str  # anxiety, depression, academic, relationships, other
    notes: Optional[str] = None
    is_anonymous: bool = False

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None  # scheduled, completed, cancelled, no_show
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    concern_type: str
    notes: Optional[str]
    is_anonymous: bool
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentDetailResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    concern_type: str
    notes: Optional[str]
    is_anonymous: bool
    status: str
    created_at: datetime
    updated_at: datetime
    slot: AppointmentSlotResponse
    
    class Config:
        from_attributes = True

class AppointmentListResponse(BaseModel):
    appointments: List[AppointmentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int