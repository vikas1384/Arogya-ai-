from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class LanguageEnum(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    KANNADA = "kannada"
    MARATHI = "marathi"
    TELUGU = "telugu"
    TAMIL = "tamil"
    BENGALI = "bengali"
    GUJARATI = "gujarati"

class ConversationStageEnum(str, Enum):
    LANGUAGE_SELECTION = "language_selection"
    GREETING = "greeting"
    SYMPTOM_INQUIRY = "symptom_inquiry"
    DETAILED_ANALYSIS = "detailed_analysis"
    HEALTH_GUIDE_GENERATION = "health_guide_generation"
    FEEDBACK = "feedback"
    EMERGENCY_ALERT = "emergency_alert"

class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

# Message Models
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    sender: str  # "user" or "dr_arogya"
    content: str
    language: Optional[LanguageEnum] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = {}

class CreateMessageRequest(BaseModel):
    content: str
    language: Optional[LanguageEnum] = None

# Session Models
class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    language: Optional[LanguageEnum] = None
    current_stage: ConversationStageEnum = ConversationStageEnum.LANGUAGE_SELECTION
    symptoms: List[str] = []
    severity_level: Optional[SeverityEnum] = None
    emergency_detected: bool = False
    health_guide_generated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class CreateSessionRequest(BaseModel):
    user_id: Optional[str] = None
    language: Optional[LanguageEnum] = None

# Health Guide Models
class TraditionalRemedy(BaseModel):
    name: str
    ingredients: List[str]
    preparation: str
    usage: str
    benefits: str
    language: LanguageEnum

class HealthGuide(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    language: LanguageEnum
    
    # Core sections from Dr. Arogya protocol
    symptom_summary: str
    possible_conditions: List[str]
    otc_recommendations: List[str]
    warning_signs: List[str]
    traditional_remedies: List[TraditionalRemedy]
    dietary_advice: List[str]
    lifestyle_tips: List[str]
    when_to_see_doctor: List[str]
    
    severity_level: SeverityEnum
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CreateHealthGuideRequest(BaseModel):
    session_id: str

# Emergency Detection Models
class EmergencyKeyword(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str
    language: LanguageEnum
    severity: SeverityEnum
    category: str  # e.g., "cardiac", "respiratory", "neurological"

# Language Support Models  
class LanguageSelection(BaseModel):
    session_id: str
    selected_language: LanguageEnum

# Feedback Models
class Feedback(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    helpful_aspects: Optional[List[str]] = []
    improvement_suggestions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CreateFeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    helpful_aspects: Optional[List[str]] = []
    improvement_suggestions: Optional[str] = None

# PDF Report Models
class PDFReportRequest(BaseModel):
    session_id: str
    include_chat_history: bool = True

class PDFReportResponse(BaseModel):
    pdf_url: str
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Response Models
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ConversationResponse(BaseModel):
    message: Message
    session: Session
    health_guide: Optional[HealthGuide] = None
    emergency_alert: bool = False