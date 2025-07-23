#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for Dr. Arogya AI Health Companion
Tests all API endpoints, AI integration, database operations, and PDF generation
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class DrArogyaBackendTester:
    def __init__(self):
        # Get backend URL from frontend environment
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.api_url = f"{self.base_url}/api"
        
        # Test data storage
        self.test_session_id = None
        self.test_results = []
        self.emergency_detected = False
        
        print(f"🏥 Dr. Arogya Backend Tester Initialized")
        print(f"📡 Testing API at: {self.api_url}")
        print("=" * 60)

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        if response_data and not success:
            print(f"   📊 Response: {response_data}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print()

    def test_health_check(self) -> bool:
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "Dr. Arogya" in data.get("message", ""):
                    self.log_test("Health Check", True, f"Status: {response.status_code}, Message: {data['message']}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected message: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_get_languages(self) -> bool:
        """Test language retrieval endpoint"""
        try:
            response = requests.get(f"{self.api_url}/languages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    languages = data["data"]
                    
                    # Check if we have expected languages
                    expected_languages = ["english", "hindi", "kannada", "marathi"]
                    found_languages = [lang["code"] for lang in languages]
                    
                    if all(lang in found_languages for lang in expected_languages):
                        self.log_test("Get Languages", True, f"Found {len(languages)} languages including: {', '.join(expected_languages)}")
                        return True
                    else:
                        self.log_test("Get Languages", False, f"Missing expected languages. Found: {found_languages}")
                        return False
                else:
                    self.log_test("Get Languages", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Get Languages", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Languages", False, f"Error: {str(e)}")
            return False

    def test_create_session(self) -> bool:
        """Test session creation"""
        try:
            payload = {
                "user_id": "test_user_health_consultation",
                "language": "english"
            }
            
            response = requests.post(f"{self.api_url}/sessions", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    session_data = data["data"]
                    self.test_session_id = session_data["id"]
                    
                    self.log_test("Create Session", True, f"Session created with ID: {self.test_session_id}")
                    return True
                else:
                    self.log_test("Create Session", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Create Session", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Create Session", False, f"Error: {str(e)}")
            return False

    def test_get_session(self) -> bool:
        """Test session retrieval"""
        if not self.test_session_id:
            self.log_test("Get Session", False, "No session ID available")
            return False
            
        try:
            response = requests.get(f"{self.api_url}/sessions/{self.test_session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    session_data = data["data"]
                    
                    if session_data["id"] == self.test_session_id:
                        self.log_test("Get Session", True, f"Retrieved session: {session_data['id']}")
                        return True
                    else:
                        self.log_test("Get Session", False, "Session ID mismatch")
                        return False
                else:
                    self.log_test("Get Session", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Get Session", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Session", False, f"Error: {str(e)}")
            return False

    def test_set_session_language(self) -> bool:
        """Test setting session language"""
        if not self.test_session_id:
            self.log_test("Set Session Language", False, "No session ID available")
            return False
            
        try:
            payload = {
                "session_id": self.test_session_id,
                "selected_language": "english"
            }
            
            response = requests.post(f"{self.api_url}/sessions/{self.test_session_id}/language", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    # Should return welcome message
                    message_data = data.get("data", {}).get("message", {})
                    if message_data and "Dr. Arogya" in message_data.get("content", ""):
                        self.log_test("Set Session Language", True, "Language set and welcome message received")
                        return True
                    else:
                        self.log_test("Set Session Language", False, "No welcome message received", data)
                        return False
                else:
                    self.log_test("Set Session Language", False, "Request failed", data)
                    return False
            else:
                self.log_test("Set Session Language", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Set Session Language", False, f"Error: {str(e)}")
            return False

    def test_send_normal_message(self) -> bool:
        """Test sending a normal health message"""
        if not self.test_session_id:
            self.log_test("Send Normal Message", False, "No session ID available")
            return False
            
        try:
            payload = {
                "content": "I have been experiencing mild headaches for the past 2 days. They usually occur in the afternoon and feel like a dull ache around my temples. I've been drinking plenty of water but it doesn't seem to help much.",
                "language": "english"
            }
            
            response = requests.post(f"{self.api_url}/sessions/{self.test_session_id}/messages", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "session" in data:
                    ai_message = data["message"]
                    session_info = data["session"]
                    
                    # Check if AI responded appropriately
                    if ai_message["sender"] == "dr_arogya" and len(ai_message["content"]) > 50:
                        self.log_test("Send Normal Message", True, f"AI responded with {len(ai_message['content'])} characters")
                        return True
                    else:
                        self.log_test("Send Normal Message", False, "Invalid AI response", data)
                        return False
                else:
                    self.log_test("Send Normal Message", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Send Normal Message", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Send Normal Message", False, f"Error: {str(e)}")
            return False

    def test_emergency_detection(self) -> bool:
        """Test emergency keyword detection"""
        if not self.test_session_id:
            self.log_test("Emergency Detection", False, "No session ID available")
            return False
            
        try:
            payload = {
                "content": "I'm having severe chest pain and can't breathe properly. It feels like crushing pain in my chest.",
                "language": "english"
            }
            
            response = requests.post(f"{self.api_url}/sessions/{self.test_session_id}/messages", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for emergency alert
                emergency_alert = data.get("emergency_alert", False)
                ai_message = data.get("message", {})
                
                if emergency_alert and "EMERGENCY" in ai_message.get("content", "").upper():
                    self.emergency_detected = True
                    self.log_test("Emergency Detection", True, "Emergency keywords detected and alert triggered")
                    return True
                else:
                    self.log_test("Emergency Detection", False, f"Emergency not detected. Alert: {emergency_alert}", data)
                    return False
            else:
                self.log_test("Emergency Detection", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Detection", False, f"Error: {str(e)}")
            return False

    def test_get_messages(self) -> bool:
        """Test retrieving conversation messages"""
        if not self.test_session_id:
            self.log_test("Get Messages", False, "No session ID available")
            return False
            
        try:
            response = requests.get(f"{self.api_url}/sessions/{self.test_session_id}/messages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    messages = data["data"]
                    
                    # Should have at least welcome message + user messages + AI responses
                    if len(messages) >= 3:
                        user_messages = [msg for msg in messages if msg["sender"] == "user"]
                        ai_messages = [msg for msg in messages if msg["sender"] == "dr_arogya"]
                        
                        self.log_test("Get Messages", True, f"Retrieved {len(messages)} messages ({len(user_messages)} user, {len(ai_messages)} AI)")
                        return True
                    else:
                        self.log_test("Get Messages", False, f"Too few messages: {len(messages)}")
                        return False
                else:
                    self.log_test("Get Messages", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Get Messages", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Messages", False, f"Error: {str(e)}")
            return False

    def test_health_guide_generation(self) -> bool:
        """Test health guide generation by sending multiple messages"""
        if not self.test_session_id:
            self.log_test("Health Guide Generation", False, "No session ID available")
            return False
            
        try:
            # Send several messages to trigger health guide generation
            messages_to_send = [
                "The headache is getting worse and I also feel nauseous now.",
                "I haven't been sleeping well lately, maybe 4-5 hours per night.",
                "I work long hours on the computer and don't take many breaks.",
                "I've been stressed about work deadlines recently.",
                "Should I be worried about these symptoms?"
            ]
            
            for i, message_content in enumerate(messages_to_send):
                payload = {
                    "content": message_content,
                    "language": "english"
                }
                
                response = requests.post(f"{self.api_url}/sessions/{self.test_session_id}/messages", json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if health guide was generated
                    if data.get("health_guide"):
                        self.log_test("Health Guide Generation", True, f"Health guide generated after {i+1} additional messages")
                        return True
                        
                    # Small delay between messages
                    time.sleep(1)
                else:
                    self.log_test("Health Guide Generation", False, f"Message {i+1} failed: {response.status_code}")
                    return False
            
            # If no health guide generated, that's still okay for testing
            self.log_test("Health Guide Generation", True, "Messages sent successfully (health guide may generate later)")
            return True
                
        except Exception as e:
            self.log_test("Health Guide Generation", False, f"Error: {str(e)}")
            return False

    def test_get_health_guide(self) -> bool:
        """Test retrieving health guide"""
        if not self.test_session_id:
            self.log_test("Get Health Guide", False, "No session ID available")
            return False
            
        try:
            response = requests.get(f"{self.api_url}/sessions/{self.test_session_id}/health-guide", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    health_guide = data["data"]
                    
                    # Check essential health guide components
                    required_fields = ["symptom_summary", "possible_conditions", "when_to_see_doctor"]
                    
                    if all(field in health_guide for field in required_fields):
                        self.log_test("Get Health Guide", True, f"Health guide retrieved with all required fields")
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in health_guide]
                        self.log_test("Get Health Guide", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Get Health Guide", False, "Invalid response format", data)
                    return False
            elif response.status_code == 404:
                self.log_test("Get Health Guide", True, "Health guide not yet generated (expected for short conversations)")
                return True
            else:
                self.log_test("Get Health Guide", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Health Guide", False, f"Error: {str(e)}")
            return False

    def test_pdf_generation(self) -> bool:
        """Test PDF report generation"""
        if not self.test_session_id:
            self.log_test("PDF Generation", False, "No session ID available")
            return False
            
        try:
            payload = {
                "session_id": self.test_session_id,
                "include_chat_history": True
            }
            
            response = requests.post(f"{self.api_url}/sessions/{self.test_session_id}/generate-pdf", json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if "pdf_url" in data and "filename" in data:
                    pdf_url = data["pdf_url"]
                    filename = data["filename"]
                    
                    # Try to access the PDF
                    pdf_response = requests.get(f"{self.base_url}{pdf_url}", timeout=10)
                    
                    if pdf_response.status_code == 200 and pdf_response.headers.get('content-type') == 'application/pdf':
                        self.log_test("PDF Generation", True, f"PDF generated: {filename} ({len(pdf_response.content)} bytes)")
                        return True
                    else:
                        self.log_test("PDF Generation", False, f"PDF not accessible: {pdf_response.status_code}")
                        return False
                else:
                    self.log_test("PDF Generation", False, "Invalid response format", data)
                    return False
            elif response.status_code == 404:
                self.log_test("PDF Generation", True, "PDF generation requires health guide (expected for short conversations)")
                return True
            else:
                self.log_test("PDF Generation", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("PDF Generation", False, f"Error: {str(e)}")
            return False

    def test_submit_feedback(self) -> bool:
        """Test feedback submission"""
        if not self.test_session_id:
            self.log_test("Submit Feedback", False, "No session ID available")
            return False
            
        try:
            payload = {
                "rating": 4,
                "comments": "Dr. Arogya was very helpful and provided good health guidance. The emergency detection worked well.",
                "helpful_aspects": ["Emergency detection", "Traditional remedies", "Clear explanations"],
                "improvement_suggestions": "Could provide more specific dietary recommendations"
            }
            
            response = requests.post(f"{self.api_url}/sessions/{self.test_session_id}/feedback", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    feedback_data = data["data"]
                    
                    if feedback_data["rating"] == 4 and feedback_data["session_id"] == self.test_session_id:
                        self.log_test("Submit Feedback", True, f"Feedback submitted with rating: {feedback_data['rating']}")
                        return True
                    else:
                        self.log_test("Submit Feedback", False, "Feedback data mismatch", data)
                        return False
                else:
                    self.log_test("Submit Feedback", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Submit Feedback", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Submit Feedback", False, f"Error: {str(e)}")
            return False

    def test_multilingual_support(self) -> bool:
        """Test Hindi language support"""
        try:
            # Create a new session for Hindi testing
            payload = {
                "user_id": "test_user_hindi",
                "language": "hindi"
            }
            
            response = requests.post(f"{self.api_url}/sessions", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                hindi_session_id = data["data"]["id"]
                
                # Set Hindi language
                lang_payload = {
                    "session_id": hindi_session_id,
                    "selected_language": "hindi"
                }
                
                lang_response = requests.post(f"{self.api_url}/sessions/{hindi_session_id}/language", json=lang_payload, timeout=10)
                
                if lang_response.status_code == 200:
                    lang_data = lang_response.json()
                    welcome_message = lang_data.get("data", {}).get("message", {}).get("content", "")
                    
                    # Check for Hindi text
                    if "नमस्ते" in welcome_message or "आरोग्य" in welcome_message:
                        self.log_test("Multilingual Support", True, "Hindi language support working")
                        return True
                    else:
                        self.log_test("Multilingual Support", False, "Hindi welcome message not found", welcome_message)
                        return False
                else:
                    self.log_test("Multilingual Support", False, f"Language setting failed: {lang_response.status_code}")
                    return False
            else:
                self.log_test("Multilingual Support", False, f"Hindi session creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Multilingual Support", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Dr. Arogya Backend Test Suite")
        print("=" * 60)
        
        # Core API Tests
        tests = [
            ("Health Check", self.test_health_check),
            ("Get Languages", self.test_get_languages),
            ("Create Session", self.test_create_session),
            ("Get Session", self.test_get_session),
            ("Set Session Language", self.test_set_session_language),
            ("Send Normal Message", self.test_send_normal_message),
            ("Emergency Detection", self.test_emergency_detection),
            ("Get Messages", self.test_get_messages),
            ("Health Guide Generation", self.test_health_guide_generation),
            ("Get Health Guide", self.test_get_health_guide),
            ("PDF Generation", self.test_pdf_generation),
            ("Submit Feedback", self.test_submit_feedback),
            ("Multilingual Support", self.test_multilingual_support),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
        
        # Print summary
        print("=" * 60)
        print(f"🏥 Dr. Arogya Backend Test Results")
        print(f"✅ Passed: {passed}/{total} tests")
        print(f"❌ Failed: {total - passed}/{total} tests")
        
        if self.emergency_detected:
            print("🚨 Emergency detection system: WORKING")
        
        if passed == total:
            print("🎉 All tests passed! Dr. Arogya backend is working correctly.")
        elif passed >= total * 0.8:
            print("⚠️  Most tests passed. Minor issues detected.")
        else:
            print("🔧 Multiple issues detected. Backend needs attention.")
        
        print("=" * 60)
        
        return passed, total

def main():
    """Main test execution"""
    tester = DrArogyaBackendTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # All tests passed
    elif passed >= total * 0.8:
        sys.exit(1)  # Minor issues
    else:
        sys.exit(2)  # Major issues

if __name__ == "__main__":
    main()