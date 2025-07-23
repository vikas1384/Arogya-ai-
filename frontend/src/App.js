import React, { useState } from "react";
import "./App.css";
import LanguageSelector from "./components/LanguageSelector";
import ChatInterface from "./components/ChatInterface";
import HealthGuide from "./components/HealthGuide";
import EmergencyAlert from "./components/EmergencyAlert";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [currentStage, setCurrentStage] = useState("language_selection");
  const [emergencyAlert, setEmergencyAlert] = useState(false);
  const [healthGuide, setHealthGuide] = useState(null);

  const handleLanguageSelected = (sessionId, language) => {
    setSessionId(sessionId);
    setSelectedLanguage(language);
    setCurrentStage("conversation");
  };

  const handleEmergencyDetected = () => {
    setEmergencyAlert(true);
    setCurrentStage("emergency");
  };

  const handleHealthGuideGenerated = (guide) => {
    setHealthGuide(guide);
    setCurrentStage("health_guide");
  };

  return (
    <div className="App min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Emergency Alert Overlay */}
      {emergencyAlert && (
        <EmergencyAlert 
          language={selectedLanguage}
          onClose={() => setEmergencyAlert(false)}
        />
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mb-4 shadow-lg">
            <span className="text-4xl">🩺</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Dr. Arogya
          </h1>
          <p className="text-lg text-gray-600">
            Your Personal AI Health Companion
          </p>
          <p className="text-sm text-indigo-600 mt-1">
            आपका व्यक्तिगत AI स्वास्थ्य साथी
          </p>
        </div>

        {/* Language Selection Stage */}
        {currentStage === "language_selection" && (
          <LanguageSelector onLanguageSelect={handleLanguageSelected} />
        )}

        {/* Conversation Stage */}
        {currentStage === "conversation" && sessionId && (
          <ChatInterface
            sessionId={sessionId}
            language={selectedLanguage}
            onEmergencyDetected={handleEmergencyDetected}
            onHealthGuideGenerated={handleHealthGuideGenerated}
          />
        )}

        {/* Health Guide Stage */}
        {currentStage === "health_guide" && healthGuide && (
          <HealthGuide
            healthGuide={healthGuide}
            sessionId={sessionId}
            language={selectedLanguage}
          />
        )}

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-2">
            🤖 Powered by AI • Made with ❤️ for your health
          </p>
          <p className="text-xs text-gray-400">
            This is an AI assistant and not a replacement for professional medical advice.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;