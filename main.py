from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import math

from ai_service import MindWellAI
from models import User, UserSession, AssessmentResult, ForumCategory, ForumPost, ForumComment, ForumLike, AppointmentSlot, Appointment, get_db
from auth import verify_password, get_password_hash, create_access_token, verify_token
from schemas import UserCreate, UserLogin, UserResponse, Token, TokenData, AssessmentSubmit, AssessmentResultResponse, AssessmentHistoryResponse, AppointmentSlotCreate, AppointmentSlotResponse, AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentDetailResponse, AppointmentListResponse
from schemas import ForumCategoryCreate, ForumCategoryResponse, ForumPostCreate, ForumPostUpdate, ForumPostResponse, ForumPostDetailResponse, ForumPostListResponse
from schemas import ForumCommentCreate, ForumCommentUpdate, ForumCommentResponse
from assessment_utils import process_assessment
import json

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MindWell AI Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")
app.mount("/js", StaticFiles(directory="."), name="js")

# Security
security = HTTPBearer()

# Initialize AI service
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")

ai_service = MindWellAI(api_key=gemini_api_key)

class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = []

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/index.html")
async def index_page():
    return FileResponse("index.html")

# HTML page routes
@app.get("/login")
async def login_page():
    return FileResponse("login.html")

@app.get("/login.html")
async def login_page_html():
    return FileResponse("login.html")

@app.get("/signup")
async def signup_page():
    return FileResponse("signup.html")

@app.get("/signup.html")
async def signup_page_html():
    return FileResponse("signup.html")

@app.get("/appointment")
async def appointment_page():
    return FileResponse("appointment.html")

@app.get("/appointment.html")
async def appointment_page_html():
    return FileResponse("appointment.html")

@app.get("/appointments")
async def appointments_page():
    return FileResponse("appointments.html")

@app.get("/appointments.html")
async def appointments_page_html():
    return FileResponse("appointments.html")

@app.get("/counselor-appointments")
async def counselor_appointments_page():
    return FileResponse("counselor_appointments.html")

@app.get("/counselor-appointments.html")
async def counselor_appointments_page_html():
    return FileResponse("counselor_appointments.html")

@app.get("/forum")
async def forum_page():
    return FileResponse("forum.html")

@app.get("/forum.html")
async def forum_page_html():
    return FileResponse("forum.html")

@app.get("/post")
async def post_page():
    return FileResponse("post.html")

@app.get("/post.html")
async def post_page_html():
    return FileResponse("post.html")

@app.get("/wellness")
async def wellness_page():
    return FileResponse("wellness_challanges.html")

@app.get("/wellness.html")
async def wellness_page_html():
    return FileResponse("wellness_challanges.html")

@app.get("/self-assessment")
async def self_assessment_page():
    return FileResponse("self_assessment.html")

@app.get("/self_assessment.html")
async def self_assessment_page_html():
    return FileResponse("self_assessment.html")

# Assessment endpoints
@app.post("/api/assessment/submit", response_model=AssessmentResultResponse)
async def submit_assessment(
    assessment: AssessmentSubmit,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Submit self-assessment and get results"""
    # Verify token
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Get user
    user = db.query(User).filter(User.email == token_data["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Process assessment
    try:
        # Extract responses in order
        responses = [r.score for r in sorted(assessment.responses, key=lambda x: x.question_id)]
        
        result = process_assessment(assessment.assessment_type, responses)
        
        # Save to database
        assessment_result = AssessmentResult(
            user_id=user.id,
            assessment_type=assessment.assessment_type,
            total_score=result["total_score"],
            severity_level=result["severity_level"],
            responses=json.dumps(result["responses"]),
            recommendations=json.dumps(result["recommendations"])
        )
        
        db.add(assessment_result)
        db.commit()
        db.refresh(assessment_result)
        
        return AssessmentResultResponse(
            id=assessment_result.id,
            assessment_type=assessment_result.assessment_type,
            total_score=assessment_result.total_score,
            severity_level=assessment_result.severity_level,
            recommendations=json.loads(assessment_result.recommendations),
            created_at=assessment_result.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/api/assessment/history", response_model=AssessmentHistoryResponse)
async def get_assessment_history(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Get user's assessment history"""
    # Verify token
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Get user
    user = db.query(User).filter(User.email == token_data["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get assessment history
    assessments = db.query(AssessmentResult).filter(
        AssessmentResult.user_id == user.id
    ).order_by(AssessmentResult.created_at.desc()).all()
    
    assessment_responses = []
    for assessment in assessments:
        assessment_responses.append(AssessmentResultResponse(
            id=assessment.id,
            assessment_type=assessment.assessment_type,
            total_score=assessment.total_score,
            severity_level=assessment.severity_level,
            recommendations=json.loads(assessment.recommendations),
            created_at=assessment.created_at
        ))
    
    return AssessmentHistoryResponse(
        assessments=assessment_responses,
        total_count=len(assessment_responses)
    )

@app.get("/api/assessment/questions/{assessment_type}")
async def get_assessment_questions(assessment_type: str):
    """Get assessment questions"""
    from assessment_utils import PHQ9_QUESTIONS, GAD7_QUESTIONS
    
    if assessment_type == "PHQ-9":
        questions = PHQ9_QUESTIONS
    elif assessment_type == "GAD-7":
        questions = GAD7_QUESTIONS
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment type"
        )
    
    return {
        "assessment_type": assessment_type,
        "questions": [
            {"id": i, "text": question} 
            for i, question in enumerate(questions)
        ],
        "instructions": "Rate how often you have been bothered by each problem over the last 2 weeks.",
        "scale": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(chat_message: ChatMessage):
    """Chat with the MindWell AI assistant"""
    try:
        logger.info(f"Received chat message: {chat_message.message[:50]}...")
        
        # Generate AI response using the enhanced service
        result = ai_service.generate_response(
            user_message=chat_message.message,
            conversation_history=chat_message.conversation_history
        )
        
        if result["status"] == "error":
            logger.error(f"AI service error: {result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "AI service error"))
        
        logger.info("AI response generated successfully")
        
        return ChatResponse(
            response=result["response"],
            suggestions=result["suggestions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Authentication endpoints
@app.post("/api/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """User registration endpoint."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        logger.info(f"New user registered: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "role": db_user.role,
                "is_active": db_user.is_active,
                "created_at": db_user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint."""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        # Verify user exists and password is correct
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user information."""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user from database
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Forum API Endpoints
@app.get("/api/forum/categories", response_model=List[ForumCategoryResponse])
async def get_forum_categories(db: Session = Depends(get_db)):
    """Get all forum categories"""
    try:
        categories = db.query(ForumCategory).order_by(ForumCategory.name).all()
        return categories
    except Exception as e:
        logger.error(f"Error fetching forum categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/forum/categories", response_model=ForumCategoryResponse)
async def create_forum_category(
    category: ForumCategoryCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new forum category (admin only)"""
    try:
        # Verify token and check if user is admin
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Create category
        db_category = ForumCategory(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        logger.info(f"New forum category created: {category.name}")
        return db_category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating forum category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/forum/posts", response_model=ForumPostListResponse)
async def get_forum_posts(
    category_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = "created_at",  # created_at, like_count, comment_count
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """Get forum posts with pagination and filtering"""
    try:
        query = db.query(ForumPost)
        
        # Filter by category if specified
        if category_id:
            query = query.filter(ForumPost.category_id == category_id)
        
        # Apply sorting
        if sort_by == "like_count":
            sort_field = ForumPost.like_count
        elif sort_by == "comment_count":
            sort_field = ForumPost.comment_count
        else:
            sort_field = ForumPost.created_at
            
        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
        
        # Apply pagination
        total_count = query.count()
        posts = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return ForumPostListResponse(
            posts=posts,
            total=total_count,
            page=page,
            per_page=per_page,
            total_pages=math.ceil(total_count / per_page)
        )
        
    except Exception as e:
        logger.error(f"Error fetching forum posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/forum/posts", response_model=ForumPostResponse)
async def create_forum_post(
    post: ForumPostCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new forum post"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if category exists
        category = db.query(ForumCategory).filter(ForumCategory.id == post.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Create post
        db_post = ForumPost(
            title=post.title,
            content=post.content,
            user_id=user.id,
            category_id=post.category_id
        )
        db.add(db_post)
        
        # Update category post count
        category.post_count += 1
        
        db.commit()
        db.refresh(db_post)
        
        logger.info(f"New forum post created: {post.title} by {user.email}")
        return db_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating forum post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/forum/posts/{post_id}", response_model=ForumPostDetailResponse)
async def get_forum_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific forum post with comments"""
    try:
        # Get post
        post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Increment view count
        post.view_count += 1
        db.commit()
        
        # Get comments
        comments = db.query(ForumComment).filter(
            ForumComment.post_id == post_id
        ).order_by(ForumComment.created_at.asc()).all()
        
        return ForumPostDetailResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            category_id=post.category_id,
            is_pinned=post.is_pinned,
            is_locked=post.is_locked,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            comments=comments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching forum post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/forum/posts/{post_id}", response_model=ForumPostResponse)
async def update_forum_post(
    post_id: int,
    post_update: ForumPostUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update a forum post (author or admin only)"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user and post
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check permissions (author or admin)
        if user.id != post.user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # Update post
        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)
        
        post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(post)
        
        logger.info(f"Forum post updated: {post_id} by {user.email}")
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating forum post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/forum/posts/{post_id}")
async def delete_forum_post(
    post_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete a forum post (author or admin only)"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user and post
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check permissions (author or admin)
        if user.id != post.user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # Get category to update post count
        category = db.query(ForumCategory).filter(ForumCategory.id == post.category_id).first()
        if category:
            category.post_count = max(0, category.post_count - 1)
        
        # Delete post (cascade will delete comments and likes)
        db.delete(post)
        db.commit()
        
        logger.info(f"Forum post deleted: {post_id} by {user.email}")
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting forum post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/forum/posts/{post_id}/comments", response_model=ForumCommentResponse)
async def create_forum_comment(
    post_id: int,
    comment: ForumCommentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a comment on a forum post"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user and post
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if post is locked
        if post.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Post is locked"
            )
        
        # Check parent comment if specified
        if comment.parent_id:
            parent_comment = db.query(ForumComment).filter(
                ForumComment.id == comment.parent_id,
                ForumComment.post_id == post_id
            ).first()
            if not parent_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found"
                )
        
        # Create comment
        db_comment = ForumComment(
            content=comment.content,
            post_id=post_id,
            user_id=user.id,
            parent_id=comment.parent_id
        )
        db.add(db_comment)
        
        # Update post comment count
        post.comment_count += 1
        
        db.commit()
        db.refresh(db_comment)
        
        logger.info(f"New forum comment created on post {post_id} by {user.email}")
        return db_comment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating forum comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/forum/posts/{post_id}/like")
async def like_forum_post(
    post_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Like or unlike a forum post"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user and post
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if user already liked the post
        existing_like = db.query(ForumLike).filter(
            ForumLike.user_id == user.id,
            ForumLike.post_id == post_id
        ).first()
        
        if existing_like:
            # Unlike the post
            db.delete(existing_like)
            post.like_count = max(0, post.like_count - 1)
            message = "Post unliked"
        else:
            # Like the post
            db_like = ForumLike(user_id=user.id, post_id=post_id)
            db.add(db_like)
            post.like_count += 1
            message = "Post liked"
        
        db.commit()
        
        logger.info(f"Forum post {post_id} {message.lower()} by {user.email}")
        return {"message": message, "like_count": post.like_count}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking forum post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Appointment API endpoints

# Get available appointment slots
@app.get("/api/appointment-slots", response_model=List[AppointmentSlotResponse])
async def get_available_slots(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AppointmentSlot).filter(AppointmentSlot.is_available == True)
    
    if date:
        try:
            from datetime import datetime
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(AppointmentSlot.date == target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    slots = query.order_by(AppointmentSlot.date, AppointmentSlot.start_time).all()
    return slots

# Book an appointment
@app.post("/api/appointments", response_model=AppointmentResponse)
async def book_appointment(
    appointment: AppointmentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if slot exists and is available
        slot = db.query(AppointmentSlot).filter(AppointmentSlot.id == appointment.slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail="Appointment slot not found")
        
        if not slot.is_available:
            raise HTTPException(status_code=400, detail="This slot is no longer available")
        
        # Check if user already has an appointment for this slot
        existing = db.query(Appointment).filter(
            Appointment.user_id == user.id,
            Appointment.slot_id == appointment.slot_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="You already have an appointment for this slot")
        
        # Create appointment
        db_appointment = Appointment(
            user_id=user.id,
            slot_id=appointment.slot_id,
            concern_type=appointment.concern_type,
            notes=appointment.notes,
            is_anonymous=appointment.is_anonymous
        )
        
        # Mark slot as unavailable
        slot.is_available = False
        
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        
        logger.info(f"New appointment booked by {user.email} for slot {appointment.slot_id}")
        return db_appointment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get user's appointments
@app.get("/api/appointments/me", response_model=List[AppointmentDetailResponse])
async def get_my_appointments(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        appointments = db.query(Appointment).filter(
            Appointment.user_id == user.id
        ).order_by(Appointment.created_at.desc()).all()
        
        return appointments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user appointments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get appointment details
@app.get("/api/appointments/{appointment_id}", response_model=AppointmentDetailResponse)
async def get_appointment(
    appointment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check if user owns this appointment or is admin/counselor
        if appointment.user_id != user.id and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view this appointment")
        
        return appointment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Update appointment
@app.put("/api/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check if user owns this appointment or is admin/counselor
        if appointment.user_id != user.id and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this appointment")
        
        # Update fields
        if appointment_update.status:
            appointment.status = appointment_update.status
        if appointment_update.notes is not None:
            appointment.notes = appointment_update.notes
        
        db.commit()
        db.refresh(appointment)
        
        logger.info(f"Appointment {appointment_id} updated by {user.email}")
        return appointment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Cancel appointment
@app.delete("/api/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check if user owns this appointment
        if appointment.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")
        
        # Mark slot as available again
        slot = db.query(AppointmentSlot).filter(AppointmentSlot.id == appointment.slot_id).first()
        if slot:
            slot.is_available = True
        
        # Delete appointment
        db.delete(appointment)
        db.commit()
        
        logger.info(f"Appointment {appointment_id} cancelled by {user.email}")
        return {"message": "Appointment cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Admin endpoints for managing appointment slots
@app.post("/api/appointment-slots", response_model=AppointmentSlotResponse)
async def create_appointment_slot(
    slot: AppointmentSlotCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is admin/counselor
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to create appointment slots")
        
        # Check for overlapping slots
        overlapping = db.query(AppointmentSlot).filter(
            AppointmentSlot.counselor_email == slot.counselor_email,
            AppointmentSlot.date == slot.date,
            AppointmentSlot.start_time < slot.end_time,
            AppointmentSlot.end_time > slot.start_time
        ).first()
        
        if overlapping:
            raise HTTPException(status_code=400, detail="Overlapping appointment slot exists")
        
        db_slot = AppointmentSlot(**slot.dict())
        db.add(db_slot)
        db.commit()
        db.refresh(db_slot)
        
        logger.info(f"New appointment slot created by {user.email}")
        return db_slot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment slot: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get counselor appointments (for counselor dashboard)
@app.get("/api/appointments/counselor")
async def get_counselor_appointments(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all appointments for the logged-in counselor"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.role != "counselor":
            raise HTTPException(status_code=403, detail="Access denied. Counselor role required.")
        
        appointments = db.query(Appointment).filter(
            Appointment.counselor_id == user.id
        ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        
        return {
            "appointments": [
                {
                    "id": appt.id,
                    "user_id": appt.user_id,
                    "user_name": appt.user.name if appt.user else None,
                    "counselor_id": appt.counselor_id,
                    "date": appt.date.isoformat(),
                    "time": appt.time.strftime("%H:%M"),
                    "duration": appt.duration,
                    "status": appt.status,
                    "concern_type": appt.concern_type,
                    "notes": appt.notes,
                    "created_at": appt.created_at.isoformat(),
                    "updated_at": appt.updated_at.isoformat()
                }
                for appt in appointments
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting counselor appointments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Add multiple time slots at once
@app.post("/api/appointments/slots")
async def add_time_slots(
    slots_request: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Add multiple time slots for a counselor"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.role != "counselor":
            raise HTTPException(status_code=403, detail="Access denied. Counselor role required.")
        
        date_str = slots_request.get("date")
        times = slots_request.get("times", [])
        duration = slots_request.get("duration", 60)
        
        if not date_str or not times:
            raise HTTPException(status_code=400, detail="Date and times are required")
        
        try:
            slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if slot_date < date.today():
                raise HTTPException(status_code=400, detail="Cannot create slots for past dates")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        created_slots = []
        
        for time_str in times:
            try:
                slot_time = datetime.strptime(time_str, "%H:%M").time()
                
                # Check if slot already exists
                existing_slot = db.query(AppointmentSlot).filter(
                    AppointmentSlot.counselor_id == user.id,
                    AppointmentSlot.date == slot_date,
                    AppointmentSlot.time == slot_time
                ).first()
                
                if existing_slot:
                    continue  # Skip duplicate slots
                
                # Create new slot
                new_slot = AppointmentSlot(
                    counselor_id=user.id,
                    date=slot_date,
                    time=slot_time,
                    duration=duration,
                    is_available=True
                )
                db.add(new_slot)
                created_slots.append(new_slot)
                
            except ValueError:
                continue  # Skip invalid time formats
        
        db.commit()
        
        return {
            "message": f"Successfully created {len(created_slots)} time slots",
            "slots_created": len(created_slots)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding time slots: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Update appointment status (for counselors)
@app.put("/api/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status_update: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update appointment status (confirm, cancel, complete)"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user
        user = db.query(User).filter(User.email == token_data["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.role != "counselor":
            raise HTTPException(status_code=403, detail="Access denied. Counselor role required.")
        
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        if appointment.counselor_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied. You can only update your own appointments.")
        
        new_status = status_update.get("status")
        valid_statuses = ["pending", "confirmed", "cancelled", "completed"]
        
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Update appointment status
        appointment.status = new_status
        appointment.updated_at = datetime.utcnow()
        
        # If cancelling, make the slot available again
        if new_status == "cancelled":
            slot = db.query(AppointmentSlot).filter(
                AppointmentSlot.id == appointment.slot_id
            ).first()
            
            if slot:
                slot.is_available = True
        
        db.commit()
        
        return {"message": "Appointment status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ai-assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)