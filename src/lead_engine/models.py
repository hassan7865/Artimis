from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String, unique=True, nullable=False)
    subreddit = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text)
    author = Column(String)
    url = Column(String)
    upvotes = Column(Integer, default=0)
    score = Column(Integer, default=0)
    intents = Column(Text)
    matched_keywords = Column(Text)
    ai_analysis = Column(Text)
    ai_outreach = Column(Text)
    status = Column(String, default="new")
    notified = Column(Boolean, default=False)
    found_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)

class ScanLog(Base):
    __tablename__ = "scan_logs"
    id = Column(Integer, primary_key=True)
    new_posts = Column(Integer)
    leads_found = Column(Integer)
    duration_sec = Column(Float)
    run_at = Column(DateTime(timezone=True), server_default=func.now())

class AiLog(Base):
    __tablename__ = "ai_logs"
    id = Column(Integer, primary_key=True)
    post_id = Column(String, nullable=False)
    input_prompt = Column(Text)
    output_response = Column(Text)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
