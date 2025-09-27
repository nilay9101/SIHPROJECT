from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mindwell.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student")  # student or admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    assessments = relationship("AssessmentResult", back_populates="user")
    appointments = relationship("Appointment", back_populates="user")
    
    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    assessment_type = Column(String, index=True)  # PHQ-9, GAD-7
    total_score = Column(Integer)
    severity_level = Column(String)  # minimal, mild, moderate, moderately_severe, severe
    responses = Column(Text)  # JSON string of question responses
    recommendations = Column(Text)  # JSON string of recommendations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assessments")

class ForumCategory(Base):
    __tablename__ = "forum_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    color = Column(String, default="#6c8ef5")  # Hex color for UI
    icon = Column(String, default="fas fa-comments")  # Font Awesome icon
    post_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = relationship("ForumPost", back_populates="category")

class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    category_id = Column(Integer, ForeignKey("forum_categories.id"), index=True)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    category = relationship("ForumCategory", back_populates="posts")
    comments = relationship("ForumComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("ForumLike", back_populates="post", cascade="all, delete-orphan")

class ForumComment(Base):
    __tablename__ = "forum_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    parent_id = Column(Integer, ForeignKey("forum_comments.id"), nullable=True)  # For nested comments
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("ForumPost", back_populates="comments")
    user = relationship("User")
    parent = relationship("ForumComment", remote_side=[id])
    replies = relationship("ForumComment", remote_side=[parent_id])
    likes = relationship("ForumLike", back_populates="comment", cascade="all, delete-orphan")

class ForumLike(Base):
    __tablename__ = "forum_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=True, index=True)
    comment_id = Column(Integer, ForeignKey("forum_comments.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    post = relationship("ForumPost", back_populates="likes")
    comment = relationship("ForumComment", back_populates="likes")
    
    # Ensure only one like per user per post/comment
    __table_args__ = (
        # Unique constraint to prevent duplicate likes
        # A user can like either a post OR a comment, not both simultaneously
        # and only once per post/comment
        {'sqlite_autoincrement': True},
    )

class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    counselor_name = Column(String(100), nullable=False)
    counselor_email = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    appointments = relationship("Appointment", back_populates="slot")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("appointment_slots.id"), nullable=False)
    concern_type = Column(String(50), nullable=False)  # anxiety, depression, academic, relationships, other
    notes = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled, no_show
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    slot = relationship("AppointmentSlot", back_populates="appointments")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()