import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import MessageBubble from "./MessageBubble";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatInterface = ({ sessionId, language, onEmergencyDetected, onHealthGuideGenerated }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [session, setSession] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetchInitialMessages();
    fetchSession();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchInitialMessages = async () => {
    try {
      const response = await axios.get(`${API}/sessions/${sessionId}/messages`);
      if (response.data.success) {
        setMessages(response.data.data);
      }
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  };

  const fetchSession = async () => {
    try {
      const response = await axios.get(`${API}/sessions/${sessionId}`);
      if (response.data.success) {
        setSession(response.data.data);
      }
    } catch (err) {
      console.error("Error fetching session:", err);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      session_id: sessionId,
      sender: "user",
      content: inputMessage,
      language: language.code,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage("");
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API}/sessions/${sessionId}/messages`, {
        content: messageToSend,
        language: language.code
      });

      if (response.data.success) {
        const { message, session: updatedSession, health_guide, emergency_alert } = response.data;
        
        setMessages(prev => [...prev, message]);
        setSession(updatedSession);

        // Handle emergency alert
        if (emergency_alert) {
          onEmergencyDetected();
          return;
        }

        // Handle health guide generation
        if (health_guide) {
          onHealthGuideGenerated(health_guide);
          return;
        }

        // Auto-focus input for next message
        setTimeout(() => {
          inputRef.current?.focus();
        }, 100);
      }
    } catch (err) {
      setError("Failed to send message. Please try again.");
      console.error("Error sending message:", err);
      
      // Remove the user message if sending failed
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getStageProgress = () => {
    if (!session) return 25;
    
    switch (session.current_stage) {
      case "greeting": return 25;
      case "symptom_inquiry": return 50;
      case "detailed_analysis": return 75;
      case "health_guide_generation": return 90;
      default: return 25;
    }
  };

  const getStageText = () => {
    if (!session) return "Starting consultation...";
    
    const stageTexts = {
      greeting: "Getting to know you",
      symptom_inquiry: "Understanding your symptoms", 
      detailed_analysis: "Analyzing your condition",
      health_guide_generation: "Preparing your health guide",
      feedback: "Ready for feedback"
    };

    return stageTexts[session.current_stage] || "In consultation";
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Bar */}
      <div className="bg-white rounded-t-2xl shadow-lg p-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600">
            Consultation Progress
          </span>
          <span className="text-sm text-indigo-600 font-semibold">
            {getStageProgress()}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-indigo-500 to-blue-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${getStageProgress()}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-500 mt-1">{getStageText()}</p>
      </div>

      {/* Chat Container */}
      <div className="bg-white shadow-xl rounded-b-2xl border border-gray-100">
        {/* Messages Area */}
        <div className="h-96 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <MessageBubble
              key={message.id || index}
              message={message}
              language={language}
            />
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-xs">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="px-6 py-2">
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-100 p-4">
          <div className="flex space-x-3">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                language.code === "hindi" 
                  ? "अपनी स्वास्थ्य समस्या के बारे में बताएं..."
                  : "Describe your health concern..."
              }
              className="flex-1 min-h-[60px] p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              rows="2"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || loading}
              className={`
                px-6 py-3 rounded-xl font-medium transition-all duration-200
                ${inputMessage.trim() && !loading
                  ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md hover:shadow-lg'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <span>Send</span>
              )}
            </button>
          </div>
          
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send • This is not a replacement for professional medical advice
          </p>
        </div>
      </div>

      {/* Tips Section */}
      <div className="mt-6 bg-blue-50 rounded-xl p-4 border border-blue-100">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
          <span className="mr-2">💡</span>
          Tips for better consultation:
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Be specific about your symptoms (location, duration, intensity)</li>
          <li>• Mention when symptoms started and what triggers them</li>
          <li>• Include any medications you're currently taking</li>
          <li>• Don't hesitate to ask follow-up questions</li>
        </ul>
      </div>
    </div>
  );
};

export default ChatInterface;