#!/usr/bin/env python3
"""
Extended Dr. Arogya Backend Test - Health Guide and PDF Generation
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')

def test_complete_health_consultation():
    """Test a complete health consultation flow including health guide and PDF generation"""
    
    base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    api_url = f"{base_url}/api"
    
    print("🏥 Testing Complete Dr. Arogya Health Consultation Flow")
    print("=" * 60)
    
    # Step 1: Create session
    print("1. Creating session...")
    session_response = requests.post(f"{api_url}/sessions", json={
        "user_id": "extended_test_user",
        "language": "english"
    })
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        return False
    
    session_id = session_response.json()["data"]["id"]
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Set language
    print("2. Setting language...")
    lang_response = requests.post(f"{api_url}/sessions/{session_id}/language", json={
        "session_id": session_id,
        "selected_language": "english"
    })
    
    if lang_response.status_code != 200:
        print(f"❌ Language setting failed: {lang_response.status_code}")
        return False
    
    print("✅ Language set to English")
    
    # Step 3: Have an extended conversation to trigger health guide generation
    print("3. Starting extended health consultation...")
    
    conversation_messages = [
        "I've been having persistent headaches for the past week. They're getting worse.",
        "The headaches are mainly on the right side of my head, like a throbbing pain.",
        "They usually start in the afternoon and last for several hours.",
        "I've also been feeling nauseous when the headaches are severe.",
        "I work long hours on the computer and have been under a lot of stress lately.",
        "I haven't been sleeping well - maybe 4-5 hours per night.",
        "I drink coffee regularly and don't drink much water during the day.",
        "The pain is about 7 out of 10 when it's at its worst.",
        "I've tried taking over-the-counter pain relievers but they don't help much.",
        "Should I be concerned about these symptoms? What should I do?"
    ]
    
    health_guide_generated = False
    
    for i, message in enumerate(conversation_messages):
        print(f"   Sending message {i+1}/10...")
        
        msg_response = requests.post(f"{api_url}/sessions/{session_id}/messages", json={
            "content": message,
            "language": "english"
        })
        
        if msg_response.status_code != 200:
            print(f"❌ Message {i+1} failed: {msg_response.status_code}")
            return False
        
        response_data = msg_response.json()
        
        # Check if health guide was generated
        if response_data.get("health_guide"):
            print(f"✅ Health guide generated after message {i+1}")
            health_guide_generated = True
            break
        
        # Small delay between messages
        time.sleep(0.5)
    
    if not health_guide_generated:
        print("⚠️  Health guide not auto-generated, checking if available...")
    
    # Step 4: Try to get health guide
    print("4. Retrieving health guide...")
    guide_response = requests.get(f"{api_url}/sessions/{session_id}/health-guide")
    
    if guide_response.status_code == 200:
        guide_data = guide_response.json()["data"]
        print("✅ Health guide retrieved successfully")
        print(f"   - Symptom summary: {guide_data['symptom_summary'][:100]}...")
        print(f"   - Possible conditions: {len(guide_data['possible_conditions'])} items")
        print(f"   - Traditional remedies: {len(guide_data['traditional_remedies'])} items")
        print(f"   - Severity level: {guide_data['severity_level']}")
        
        # Step 5: Generate PDF report
        print("5. Generating PDF report...")
        pdf_response = requests.post(f"{api_url}/sessions/{session_id}/generate-pdf", json={
            "session_id": session_id,
            "include_chat_history": True
        })
        
        if pdf_response.status_code == 200:
            pdf_data = pdf_response.json()
            pdf_url = pdf_data["pdf_url"]
            filename = pdf_data["filename"]
            
            print(f"✅ PDF generated: {filename}")
            
            # Try to download the PDF
            download_response = requests.get(f"{base_url}{pdf_url}")
            
            if download_response.status_code == 200 and download_response.headers.get('content-type') == 'application/pdf':
                print(f"✅ PDF download successful ({len(download_response.content)} bytes)")
                
                # Step 6: Submit feedback
                print("6. Submitting feedback...")
                feedback_response = requests.post(f"{api_url}/sessions/{session_id}/feedback", json={
                    "rating": 5,
                    "comments": "Excellent consultation! The health guide was very comprehensive and the PDF report will be helpful for my doctor visit.",
                    "helpful_aspects": ["Detailed health guide", "Traditional remedies", "PDF report", "Emergency detection"],
                    "improvement_suggestions": "Maybe add more dietary recommendations"
                })
                
                if feedback_response.status_code == 200:
                    print("✅ Feedback submitted successfully")
                    
                    print("\n" + "=" * 60)
                    print("🎉 COMPLETE HEALTH CONSULTATION TEST PASSED!")
                    print("✅ All features working: Session, Conversation, Health Guide, PDF, Feedback")
                    print("=" * 60)
                    return True
                else:
                    print(f"❌ Feedback submission failed: {feedback_response.status_code}")
                    return False
            else:
                print(f"❌ PDF download failed: {download_response.status_code}")
                return False
        else:
            print(f"❌ PDF generation failed: {pdf_response.status_code}")
            return False
    else:
        print(f"❌ Health guide retrieval failed: {guide_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_complete_health_consultation()
    exit(0 if success else 1)