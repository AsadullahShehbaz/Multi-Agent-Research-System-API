from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time

from app.database.db import get_db
from app.database.models import User, ResearchSession
from app.auth.dependencies import get_current_user
from app.agent.graph import research
from app.api.models import ResearchRequest, ResearchResponse, ResearchHistoryItem
router = APIRouter(prefix="/research", tags=["Research"])

@router.post("/", response_model=ResearchResponse)
def create_research(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new research query
    
    Requires authentication. The multi-agent system will:
    1. Research the topic
    2. Fact-check the findings
    3. Generate a comprehensive report
    
    Results are saved to your account.
    """
    # Create session in database
    research_session = ResearchSession(
        user_id=current_user.id,
        query=request.query,
        status="processing"
    )
    db.add(research_session)
    db.commit()
    db.refresh(research_session)
    
    try:
        # Run multi-agent research
        start_time = time.time()
        result = research(request.query)
        processing_time = int(time.time() - start_time)
        
        # Update session with results
        research_session.research_data = result["research_data"]
        research_session.verified_facts = result["verified_facts"]
        research_session.final_report = result["final_report"]
        research_session.status = "completed"
        research_session.processing_time = processing_time
        research_session.completed_at = datetime.now()
        
        db.commit()
        db.refresh(research_session)
        
        return {
            "id": research_session.id,
            "query": research_session.query,
            "research_data": research_session.research_data,
            "verified_facts": research_session.verified_facts,
            "final_report": research_session.final_report,
            "status": research_session.status,
            "processing_time": research_session.processing_time,
            "created_at": str(research_session.created_at)
        }
        
    except Exception as e:
        # Update status to failed
        research_session.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@router.get("/history", response_model=List[ResearchHistoryItem])
def get_research_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get your research history
    
    Returns list of all your past research queries.
    Use skip and limit for pagination.
    """
    sessions = db.query(ResearchSession)\
        .filter(ResearchSession.user_id == current_user.id)\
        .order_by(ResearchSession.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": s.id,
            "query": s.query,
            "status": s.status,
            "created_at": str(s.created_at),
            "processing_time": s.processing_time
        }
        for s in sessions
    ]

@router.get("/{research_id}", response_model=ResearchResponse)
def get_research_by_id(
    research_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific research by ID
    
    Returns full details of a research session.
    You can only access your own research.
    """
    session = db.query(ResearchSession)\
        .filter(
            ResearchSession.id == research_id,
            ResearchSession.user_id == current_user.id
        )\
        .first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Research not found")
    
    return {
        "id": session.id,
        "query": session.query,
        "research_data": session.research_data or "",
        "verified_facts": session.verified_facts or "",
        "final_report": session.final_report or "",
        "status": session.status,
        "processing_time": session.processing_time,
        "created_at": str(session.created_at)
    }

@router.delete("/{research_id}")
def delete_research(
    research_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a research session"""
    session = db.query(ResearchSession)\
        .filter(
            ResearchSession.id == research_id,
            ResearchSession.user_id == current_user.id
        )\
        .first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Research not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Research deleted successfully"}

