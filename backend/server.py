from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime

# Import Dr. Arogya modules
from models import (
    Session, Message, HealthGuide, Feedback,
    CreateSessionRequest, CreateMessageRequest, CreateFeedbackRequest, 
    PDFReportRequest, PDFReportResponse, ConversationResponse,
    LanguageEnum, ConversationStageEnum, SeverityEnum,
    LanguageSelection, ApiResponse
)
from dr_arogya_service import DrArogyaService
from pdf_service import PDFService


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Dr. Arogya - AI Health Companion API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
dr_arogya_service = DrArogyaService()
pdf_service = PDFService()

# Serve static files for PDF downloads
app.mount("/reports", StaticFiles(directory="/app/backend/reports"), name="reports")

# Basic status endpoint
@api_router.get("/")
async def root():
    return {"message": "Dr. Arogya AI Health Companion - Ready to Help! 🏥"}

# === LANGUAGE SELECTION ENDPOINTS ===

@api_router.get("/languages")
async def get_available_languages():
    """Get list of supported languages"""
    languages = [
        {"code": LanguageEnum.ENGLISH, "name": "English", "native_name": "English"},
        {"code": LanguageEnum.HINDI, "name": "Hindi", "native_name": "हिन्दी"},
        {"code": LanguageEnum.KANNADA, "name": "Kannada", "native_name": "ಕನ್ನಡ"},
        {"code": LanguageEnum.MARATHI, "name": "Marathi", "native_name": "मराठी"},
        {"code": LanguageEnum.TELUGU, "name": "Telugu", "native_name": "తెలుగు"},
        {"code": LanguageEnum.TAMIL, "name": "Tamil", "native_name": "தமிழ்"},
        {"code": LanguageEnum.BENGALI, "name": "Bengali", "native_name": "বাংলা"},
        {"code": LanguageEnum.GUJARATI, "name": "Gujarati", "native_name": "ગુજરાતી"},
    ]
    return ApiResponse(success=True, message="Languages retrieved", data=languages)

# === SESSION MANAGEMENT ENDPOINTS ===

@api_router.post("/sessions", response_model=ApiResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new consultation session"""
    try:
        session = Session(
            user_id=request.user_id,
            language=request.language
        )
        
        await db.sessions.insert_one(session.dict())
        
        return ApiResponse(
            success=True,
            message="Session created successfully",
            data=session
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@api_router.get("/sessions/{session_id}", response_model=ApiResponse)
async def get_session(session_id: str):
    """Get session details"""
    try:
        session_data = await db.sessions.find_one({"id": session_id})
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = Session(**session_data)
        
        return ApiResponse(
            success=True,
            message="Session retrieved",
            data=session
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@api_router.post("/sessions/{session_id}/language", response_model=ApiResponse)
async def set_session_language(session_id: str, language_selection: LanguageSelection):
    """Set language for session"""
    try:
        session_data = await db.sessions.find_one({"id": session_id})
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session language and stage
        await db.sessions.update_one(
            {"id": session_id},
            {
                "$set": {
                    "language": language_selection.selected_language,
                    "current_stage": ConversationStageEnum.GREETING,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Generate welcome message
        if language_selection.selected_language == LanguageEnum.HINDI:
            welcome_message = """नमस्ते! 🙏 मैं डॉ. आरोग्य हूं, आपका व्यक्तिगत स्वास्थ्य सहायक।

मुझे आपकी स्वास्थ्य संबंधी समस्या समझने और आपको बेहतर महसूस कराने में खुशी होगी।

मैं आपसे कुछ सवाल पूछूंगा ताकि आपकी स्थिति को बेहतर तरीके से समझ सकूं। इसके बाद, मैं आपके लिए एक पूरा स्वास्थ्य गाइड तैयार करूंगा जो आपको डॉक्टर के पास जाने के लिए तैयार करेगा।

⚠️ महत्वपूर्ण: मैं एक AI सहायक हूं, डॉक्टर नहीं। यदि यह मेडिकल इमरजेंसी है, तो कृपया तुरंत नजदीकी अस्पताल जाएं।

कृपया अपनी स्वास्थ्य समस्या के बारे में बताएं।"""
        else:
            welcome_message = """Hello! 🙏 I'm Dr. Arogya, your personal health assistant.

I'm here to help you understand your health concerns and feel better.

I'll ask you a few questions to understand your condition better. Based on your answers, I will prepare a complete health guide to help you feel more prepared for your doctor's visit. This will include potential next steps, lifestyle advice, and even some trusted दादी माँ के नुस्खे (grandmother's remedies).

⚠️ Important: I am an AI assistant, not a human doctor. If this is a medical emergency, please stop now and call your nearest hospital immediately.

Please tell me about your health concern."""
        
        # Create welcome message
        welcome_msg = Message(
            session_id=session_id,
            sender="dr_arogya",
            content=welcome_message,
            language=language_selection.selected_language
        )
        
        await db.messages.insert_one(welcome_msg.dict())
        
        return ApiResponse(
            success=True,
            message="Language set successfully",
            data={"message": welcome_msg}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting language: {str(e)}")

# === CONVERSATION ENDPOINTS ===

@api_router.post("/sessions/{session_id}/messages", response_model=ConversationResponse)
async def send_message(session_id: str, request: CreateMessageRequest):
    """Send message in conversation"""
    try:
        # Get session
        session_data = await db.sessions.find_one({"id": session_id})
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = Session(**session_data)
        
        # Create user message
        user_message = Message(
            session_id=session_id,
            sender="user",
            content=request.content,
            language=request.language or session.language
        )
        
        # Store user message
        await db.messages.insert_one(user_message.dict())
        
        # Generate AI response
        ai_response_text, emergency_detected = await dr_arogya_service.generate_response(
            session, request.content
        )
        
        # Update session if emergency detected
        if emergency_detected:
            await db.sessions.update_one(
                {"id": session_id},
                {
                    "$set": {
                        "emergency_detected": True,
                        "severity_level": SeverityEnum.EMERGENCY,
                        "current_stage": ConversationStageEnum.EMERGENCY_ALERT,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            session.emergency_detected = True
            session.severity_level = SeverityEnum.EMERGENCY
            session.current_stage = ConversationStageEnum.EMERGENCY_ALERT
        else:
            # Update conversation stage based on content
            new_stage = await _determine_conversation_stage(session, request.content)
            
            await db.sessions.update_one(
                {"id": session_id},
                {
                    "$set": {
                        "current_stage": new_stage,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            session.current_stage = new_stage
        
        # Create AI response message
        ai_message = Message(
            session_id=session_id,
            sender="dr_arogya",
            content=ai_response_text,
            language=session.language
        )
        
        # Store AI message
        await db.messages.insert_one(ai_message.dict())
        
        # Generate health guide if conversation is complete
        health_guide = None
        if session.current_stage == ConversationStageEnum.HEALTH_GUIDE_GENERATION:
            messages = await db.messages.find({"session_id": session_id}).to_list(1000)
            message_objects = [Message(**msg) for msg in messages]
            
            health_guide = await dr_arogya_service.generate_health_guide(session, message_objects)
            await db.health_guides.insert_one(health_guide.dict())
            
            # Update session
            await db.sessions.update_one(
                {"id": session_id},
                {
                    "$set": {
                        "health_guide_generated": True,
                        "current_stage": ConversationStageEnum.FEEDBACK,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        return ConversationResponse(
            message=ai_message,
            session=session,
            health_guide=health_guide,
            emergency_alert=emergency_detected
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@api_router.get("/sessions/{session_id}/messages", response_model=ApiResponse)
async def get_session_messages(session_id: str):
    """Get all messages for a session"""
    try:
        messages_data = await db.messages.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
        messages = [Message(**msg) for msg in messages_data]
        
        return ApiResponse(
            success=True,
            message="Messages retrieved",
            data=messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

# === HEALTH GUIDE ENDPOINTS ===

@api_router.get("/sessions/{session_id}/health-guide", response_model=ApiResponse)
async def get_health_guide(session_id: str):
    """Get health guide for session"""
    try:
        guide_data = await db.health_guides.find_one({"session_id": session_id})
        
        if not guide_data:
            raise HTTPException(status_code=404, detail="Health guide not found")
        
        health_guide = HealthGuide(**guide_data)
        
        return ApiResponse(
            success=True,
            message="Health guide retrieved",
            data=health_guide
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving health guide: {str(e)}")

# === PDF GENERATION ENDPOINTS ===

@api_router.post("/sessions/{session_id}/generate-pdf", response_model=PDFReportResponse)
async def generate_pdf_report(session_id: str, request: PDFReportRequest):
    """Generate PDF health report"""
    try:
        # Get session
        session_data = await db.sessions.find_one({"id": session_id})
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = Session(**session_data)
        
        # Get health guide
        guide_data = await db.health_guides.find_one({"session_id": session_id})
        if not guide_data:
            raise HTTPException(status_code=404, detail="Health guide not found")
        
        health_guide = HealthGuide(**guide_data)
        
        # Get messages if requested
        messages = None
        if request.include_chat_history:
            messages_data = await db.messages.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
            messages = [Message(**msg) for msg in messages_data]
        
        # Generate PDF
        filename = pdf_service.generate_health_report(
            session, health_guide, messages, request.include_chat_history
        )
        
        pdf_url = f"/reports/{filename}"
        
        return PDFReportResponse(
            pdf_url=pdf_url,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/reports/{filename}")
async def download_pdf_report(filename: str):
    """Download PDF report"""
    try:
        filepath = pdf_service.get_report_path(filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")

# === FEEDBACK ENDPOINTS ===

@api_router.post("/sessions/{session_id}/feedback", response_model=ApiResponse)
async def submit_feedback(session_id: str, request: CreateFeedbackRequest):
    """Submit feedback for session"""
    try:
        feedback = Feedback(
            session_id=session_id,
            rating=request.rating,
            comments=request.comments,
            helpful_aspects=request.helpful_aspects,
            improvement_suggestions=request.improvement_suggestions
        )
        
        await db.feedback.insert_one(feedback.dict())
        
        return ApiResponse(
            success=True,
            message="Feedback submitted successfully",
            data=feedback
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

# === UTILITY FUNCTIONS ===

async def _determine_conversation_stage(session: Session, user_message: str) -> ConversationStageEnum:
    """Determine next conversation stage based on current stage and user input"""
    
    current_stage = session.current_stage
    message_lower = user_message.lower()
    
    # Simple stage progression logic
    if current_stage == ConversationStageEnum.GREETING:
        return ConversationStageEnum.SYMPTOM_INQUIRY
    elif current_stage == ConversationStageEnum.SYMPTOM_INQUIRY:
        # Check if we have enough information (simple heuristic)
        if len(user_message.split()) > 10:  # Detailed response
            return ConversationStageEnum.DETAILED_ANALYSIS
        else:
            return ConversationStageEnum.SYMPTOM_INQUIRY
    elif current_stage == ConversationStageEnum.DETAILED_ANALYSIS:
        # After a few exchanges, move to health guide generation
        message_count = await db.messages.count_documents({"session_id": session.id})
        if message_count > 8:  # After some back and forth
            return ConversationStageEnum.HEALTH_GUIDE_GENERATION
        else:
            return ConversationStageEnum.DETAILED_ANALYSIS
    
    return current_stage

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db_client():
    logger.info("Dr. Arogya AI Health Companion - Starting up! 🏥")
    # Cleanup old PDF reports on startup
    pdf_service.cleanup_old_reports()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Dr. Arogya AI Health Companion - Shutting down! 👋")
