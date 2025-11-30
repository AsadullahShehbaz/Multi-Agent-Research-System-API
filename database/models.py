from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User table - stores registered users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship: One user can have many research sessions
    research_sessions = relationship("ResearchSession", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class ResearchSession(Base):
    """Research sessions - stores all research queries and results"""
    __tablename__ = "research_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    
    # Agent outputs
    research_data = Column(Text)
    verified_facts = Column(Text)
    final_report = Column(Text)
    
    # Metadata
    status = Column(String, default="pending")  # pending, completed, failed
    agent_iterations = Column(Integer, default=0)
    processing_time = Column(Integer)  # seconds
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    
    # Relationship
    user = relationship("User", back_populates="research_sessions")
    
    def __repr__(self):
        return f"<ResearchSession {self.id}: {self.query[:30]}>"
