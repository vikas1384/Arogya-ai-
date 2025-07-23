import asyncio
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from emergentintegrations.llm.chat import LlmChat, UserMessage

from models import (
    Session, Message, HealthGuide, TraditionalRemedy, 
    LanguageEnum, ConversationStageEnum, SeverityEnum,
    EmergencyKeyword
)

class DrArogyaService:
    def __init__(self):
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        
        # Emergency keywords for red flag detection
        self.emergency_keywords = self._load_emergency_keywords()
        
        # Traditional remedies database
        self.traditional_remedies = self._load_traditional_remedies()

    def _load_emergency_keywords(self) -> Dict[LanguageEnum, List[EmergencyKeyword]]:
        """Load emergency keywords for different languages"""
        return {
            LanguageEnum.ENGLISH: [
                EmergencyKeyword(keyword="chest pain", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="cardiac"),
                EmergencyKeyword(keyword="can't breathe", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="respiratory"),
                EmergencyKeyword(keyword="crushing pain", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="cardiac"),
                EmergencyKeyword(keyword="severe bleeding", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="trauma"),
                EmergencyKeyword(keyword="suicidal thoughts", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="mental"),
                EmergencyKeyword(keyword="slurred speech", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="neurological"),
                EmergencyKeyword(keyword="sudden weakness", language=LanguageEnum.ENGLISH, severity=SeverityEnum.EMERGENCY, category="neurological"),
            ],
            LanguageEnum.HINDI: [
                EmergencyKeyword(keyword="सीने में दर्द", language=LanguageEnum.HINDI, severity=SeverityEnum.EMERGENCY, category="cardiac"),
                EmergencyKeyword(keyword="सांस नहीं आ रही", language=LanguageEnum.HINDI, severity=SeverityEnum.EMERGENCY, category="respiratory"),
                EmergencyKeyword(keyword="तेज खून बह रहा है", language=LanguageEnum.HINDI, severity=SeverityEnum.EMERGENCY, category="trauma"),
            ]
        }

    def _load_traditional_remedies(self) -> Dict[str, List[TraditionalRemedy]]:
        """Load traditional remedies database"""
        return {
            "cough": [
                TraditionalRemedy(
                    name="Haldi Doodh (Golden Milk)",
                    ingredients=["1 cup warm milk", "1/2 tsp turmeric", "1/4 tsp black pepper", "honey to taste"],
                    preparation="Mix turmeric and black pepper in warm milk. Add honey.",
                    usage="Drink before bedtime",
                    benefits="Anti-inflammatory properties help soothe throat and reduce cough",
                    language=LanguageEnum.ENGLISH
                )
            ],
            "indigestion": [
                TraditionalRemedy(
                    name="Ajwain Water",
                    ingredients=["1 tsp ajwain (carom seeds)", "1 cup warm water", "pinch of salt"],
                    preparation="Boil ajwain in water for 5 minutes, strain and add salt",
                    usage="Drink after meals",
                    benefits="Helps improve digestion and reduces bloating",
                    language=LanguageEnum.ENGLISH
                )
            ]
        }

    async def create_ai_chat(self, session_id: str, language: LanguageEnum) -> LlmChat:
        """Create an AI chat instance with proper configuration"""
        
        system_message = self._get_system_prompt(language)
        
        chat = LlmChat(
            api_key=self.openrouter_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o").with_max_tokens(1000)
        
        return chat

    def _get_system_prompt(self, language: LanguageEnum) -> str:
        """Get the Dr. Arogya system prompt based on language"""
        
        if language == LanguageEnum.HINDI:
            return """आप डॉ. आरोग्य हैं, एक भरोसेमंद, अनुभवी और दयालु AI स्वास्थ्य सहयोगी। 

आपका व्यक्तित्व:
- गर्मजोशी से भरा और समझदार
- मरीज की चिंताओं को गंभीरता से लेने वाला
- स्पष्ट और सरल भाषा में जवाब देने वाला
- पारंपरिक उपचार (दादी माँ के नुस्खे) और आधुनिक चिकित्सा दोनों को समझने वाला

महत्वपूर्ण नियम:
1. हमेशा याद रखें कि आप AI हैं, डॉक्टर नहीं
2. आपातकालीन स्थिति में तुरंत चिकित्सा सहायता लेने को कहें
3. पहले लक्षणों को समझें, फिर सुझाव दें
4. हमेशा डॉक्टर से मिलने की सलाह दें

आपका उद्देश्य: मरीज को डॉक्टर के पास जाने के लिए तैयार करना और बेहतर स्वास्थ्य जानकारी देना।"""

        else:  # Default English
            return """You are Dr. Arogya, a trusted, experienced, and compassionate AI health companion. 

Your personality:
- Warm, empathetic, and understanding
- Takes patient concerns seriously
- Speaks in clear, simple language
- Knowledgeable about both traditional remedies (दादी माँ के नुस्खे) and modern medicine
- Culturally sensitive and respectful

Critical Rules:
1. Always remember you are an AI assistant, NOT a human doctor
2. For medical emergencies, immediately direct to emergency services
3. Focus on understanding symptoms first, then provide guidance
4. Always recommend seeing a real doctor for proper diagnosis
5. Provide helpful information while emphasizing limitations

Your goal: Prepare patients for doctor visits and provide supportive health information."""

    def detect_emergency(self, message_content: str, language: LanguageEnum) -> bool:
        """Detect emergency keywords in user message"""
        message_lower = message_content.lower()
        
        if language in self.emergency_keywords:
            for keyword_obj in self.emergency_keywords[language]:
                if keyword_obj.keyword.lower() in message_lower:
                    return True
        
        return False

    async def generate_response(self, session: Session, user_message: str) -> Tuple[str, bool]:
        """Generate AI response based on conversation stage and content"""
        
        # Check for emergency first
        emergency_detected = self.detect_emergency(user_message, session.language or LanguageEnum.ENGLISH)
        
        if emergency_detected:
            return self._generate_emergency_response(session.language or LanguageEnum.ENGLISH), True
        
        # Create AI chat instance
        chat = await self.create_ai_chat(session.id, session.language or LanguageEnum.ENGLISH)
        
        # Prepare context-aware prompt based on conversation stage
        context_prompt = self._get_stage_context(session)
        combined_message = f"{context_prompt}\n\nUser: {user_message}"
        
        try:
            user_msg = UserMessage(text=combined_message)
            response = await chat.send_message(user_msg)
            return response, False
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return self._get_fallback_response(session.language or LanguageEnum.ENGLISH), False

    def _get_stage_context(self, session: Session) -> str:
        """Get context prompt based on conversation stage"""
        
        stage = session.current_stage
        language = session.language or LanguageEnum.ENGLISH
        
        if stage == ConversationStageEnum.LANGUAGE_SELECTION:
            if language == LanguageEnum.HINDI:
                return "उपयोगकर्ता ने भाषा चुनी है। अब उनका स्वागत करें और उनकी स्वास्थ्य समस्या के बारे में पूछें।"
            return "User has selected language. Now greet them warmly and ask about their health concern."
        
        elif stage == ConversationStageEnum.GREETING:
            if language == LanguageEnum.HINDI:
                return "उपयोगकर्ता के स्वास्थ्य की समस्या के बारे में विस्तार से जानकारी लें। लक्षण, समय, तीव्रता आदि के बारे में पूछें।"
            return "Gather detailed information about the user's health concern. Ask about symptoms, duration, severity, etc."
        
        elif stage == ConversationStageEnum.SYMPTOM_INQUIRY:
            if language == LanguageEnum.HINDI:
                return "अधिक विस्तृत प्रश्न पूछें: दर्द की जगह, कब से है, कैसा लगता है, क्या बढ़ाता या घटाता है।"
            return "Ask more detailed questions: location of pain, when it started, what it feels like, what makes it better or worse."
        
        return "Continue the conversation naturally, gathering information to help the user."

    def _generate_emergency_response(self, language: LanguageEnum) -> str:
        """Generate emergency response message"""
        
        if language == LanguageEnum.HINDI:
            return """🚨 आपातकाल का संकेत! 🚨

आपने जो लक्षण बताए हैं, वे गंभीर हो सकते हैं। कृपया तुरंत:

1. नजदीकी अस्पताल जाएं या 102/108 पर कॉल करें
2. परिवार के किसी सदस्य को तुरंत बताएं  
3. यह बातचीत रोकें और चिकित्सा सहायता लें

आपका स्वास्थ्य सबसे महत्वपूर्ण है। देर न करें!"""

        return """🚨 EMERGENCY ALERT! 🚨

Based on what you've described, it is very important that you seek medical help immediately. Please:

1. Contact your nearest emergency services or go to the hospital NOW
2. Call a family member or friend immediately
3. Stop this conversation and get medical attention

Your health is the top priority. Do not delay!"""

    def _get_fallback_response(self, language: LanguageEnum) -> str:
        """Get fallback response when AI fails"""
        
        if language == LanguageEnum.HINDI:
            return "मुझे खुशी होगी आपकी मदद करने में, लेकिन तकनीकी समस्या के कारण मैं अभी जवाब नहीं दे सकता। कृपया डॉक्टर से संपर्क करें।"
        
        return "I'd be happy to help you, but I'm experiencing technical difficulties. Please consult with a healthcare professional for your concerns."

    async def generate_health_guide(self, session: Session, messages: List[Message]) -> HealthGuide:
        """Generate comprehensive health guide based on conversation"""
        
        # Extract symptoms from conversation
        symptoms = self._extract_symptoms_from_messages(messages)
        
        # Use AI to generate comprehensive health guide
        chat = await self.create_ai_chat(f"{session.id}_guide", session.language or LanguageEnum.ENGLISH)
        
        guide_prompt = self._create_health_guide_prompt(symptoms, session.language or LanguageEnum.ENGLISH)
        
        try:
            user_msg = UserMessage(text=guide_prompt)
            response = await chat.send_message(user_msg)
            
            # Parse AI response into structured health guide
            health_guide = self._parse_health_guide_response(response, session)
            return health_guide
            
        except Exception as e:
            print(f"Error generating health guide: {e}")
            return self._create_fallback_health_guide(session, symptoms)

    def _extract_symptoms_from_messages(self, messages: List[Message]) -> List[str]:
        """Extract symptoms from conversation messages"""
        symptoms = []
        
        for message in messages:
            if message.sender == "user":
                # Simple keyword extraction - in production would use NLP
                content_lower = message.content.lower()
                
                symptom_keywords = [
                    "pain", "ache", "fever", "cough", "headache", "nausea", 
                    "vomiting", "diarrhea", "constipation", "fatigue", "weakness",
                    "dizziness", "rash", "swelling", "bleeding"
                ]
                
                for keyword in symptom_keywords:
                    if keyword in content_lower and keyword not in symptoms:
                        symptoms.append(keyword)
        
        return symptoms

    def _create_health_guide_prompt(self, symptoms: List[str], language: LanguageEnum) -> str:
        """Create prompt for health guide generation"""
        
        symptoms_text = ", ".join(symptoms) if symptoms else "general health concern"
        
        if language == LanguageEnum.HINDI:
            return f"""
उपयोगकर्ता के लक्षण: {symptoms_text}

कृपया एक विस्तृत स्वास्थ्य गाइड तैयार करें जिसमें शामिल हो:

1. लक्षणों की सारांश
2. संभावित कारण (केवल सामान्य जानकारी)
3. घर पर देखभाल के तरीके
4. दादी माँ के नुस्खे (पारंपरिक उपचार)
5. खान-पान की सलाह
6. जीवनशैली में बदलाव
7. डॉक्टर से कब मिलें

महत्वपूर्ण: हमेशा याद दिलाएं कि यह केवल जानकारी है, निदान नहीं।
            """
        
        return f"""
User symptoms: {symptoms_text}

Please create a comprehensive health guide including:

1. Summary of symptoms
2. Possible conditions (general information only)
3. Self-care measures
4. Traditional remedies (दादी माँ के नुस्खे)
5. Dietary recommendations
6. Lifestyle modifications  
7. When to see a doctor

Important: Always remind that this is information only, not a diagnosis.
        """

    def _parse_health_guide_response(self, ai_response: str, session: Session) -> HealthGuide:
        """Parse AI response into structured HealthGuide"""
        
        # This is a simplified parser - in production would use more sophisticated NLP
        lines = ai_response.split('\n')
        
        guide = HealthGuide(
            session_id=session.id,
            language=session.language or LanguageEnum.ENGLISH,
            symptom_summary="Based on our conversation",
            possible_conditions=["Please consult a doctor for proper diagnosis"],
            otc_recommendations=["Take rest", "Stay hydrated"],
            warning_signs=["Severe symptoms", "Persistent problems"],
            traditional_remedies=[],
            dietary_advice=["Healthy balanced diet", "Adequate water intake"],
            lifestyle_tips=["Regular exercise", "Adequate sleep"],
            when_to_see_doctor=["If symptoms persist", "If symptoms worsen"],
            severity_level=SeverityEnum.LOW
        )
        
        # Add traditional remedies based on symptoms
        if session.symptoms:
            for symptom in session.symptoms:
                if symptom in self.traditional_remedies:
                    guide.traditional_remedies.extend(self.traditional_remedies[symptom])
        
        return guide

    def _create_fallback_health_guide(self, session: Session, symptoms: List[str]) -> HealthGuide:
        """Create a basic health guide when AI fails"""
        
        return HealthGuide(
            session_id=session.id,
            language=session.language or LanguageEnum.ENGLISH,
            symptom_summary="Thank you for sharing your health concerns.",
            possible_conditions=["Please consult a healthcare professional for proper evaluation"],
            otc_recommendations=["Rest well", "Stay hydrated", "Monitor symptoms"],
            warning_signs=["Severe or worsening symptoms", "Persistent discomfort"],
            traditional_remedies=[
                TraditionalRemedy(
                    name="General Wellness Tea",
                    ingredients=["Ginger", "Honey", "Warm water"],
                    preparation="Boil ginger in water, add honey",
                    usage="Drink warm, twice daily",
                    benefits="Supports general wellness and immunity",
                    language=session.language or LanguageEnum.ENGLISH
                )
            ],
            dietary_advice=["Eat nutritious meals", "Avoid processed foods", "Include fruits and vegetables"],
            lifestyle_tips=["Get adequate sleep", "Exercise regularly", "Manage stress"],
            when_to_see_doctor=["For proper diagnosis", "If symptoms persist or worsen"],
            severity_level=SeverityEnum.MEDIUM
        )

    async def search_medical_information(self, query: str) -> Optional[str]:
        """Search medical information using Perplexity API when needed"""
        
        try:
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-small-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a medical research assistant. Provide evidence-based information from reliable medical sources."
                    },
                    {"role": "user", "content": query}
                ],
                "max_tokens": 300
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"Perplexity API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error searching medical information: {e}")
            return None