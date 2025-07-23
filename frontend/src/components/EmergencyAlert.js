import React from "react";

const EmergencyAlert = ({ language, onClose }) => {
  const getEmergencyText = () => {
    if (language?.code === "hindi") {
      return {
        title: "🚨 आपातकाल का संकेत! 🚨",
        message: `आपने जो लक्षण बताए हैं, वे गंभीर हो सकते हैं। कृपया तुरंत:

1. नजदीकी अस्पताल जाएं या 102/108 पर कॉल करें
2. परिवार के किसी सदस्य को तुरंत बताएं  
3. यह बातचीत रोकें और चिकित्सा सहायता लें

आपका स्वास्थ्य सबसे महत्वपूर्ण है। देर न करें!`,
        callButton: "102/108 पर कॉल करें",
        hospitalButton: "अस्पताल खोजें"
      };
    }
    
    return {
      title: "🚨 EMERGENCY ALERT! 🚨",
      message: `Based on what you've described, it is very important that you seek medical help immediately. Please:

1. Contact your nearest emergency services or go to the hospital NOW
2. Call a family member or friend immediately
3. Stop this conversation and get medical attention

Your health is the top priority. Do not delay!`,
      callButton: "Call Emergency",
      hospitalButton: "Find Hospital"
    };
  };

  const { title, message, callButton, hospitalButton } = getEmergencyText();

  const handleEmergencyCall = () => {
    if (language?.code === "hindi") {
      window.open("tel:102", "_self");
    } else {
      window.open("tel:911", "_self"); // Adjust based on country
    }
  };

  const handleFindHospital = () => {
    window.open("https://www.google.com/maps/search/hospital+near+me", "_blank");
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-pulse-ring">
        {/* Animated Ring Effect */}
        <div className="absolute inset-0 rounded-2xl border-4 border-red-500 animate-ping"></div>
        
        <div className="relative bg-red-50 rounded-2xl border-4 border-red-500 p-6">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="text-6xl mb-4 animate-bounce">🚨</div>
            <h2 className="text-2xl font-bold text-red-800 mb-2">
              {title}
            </h2>
          </div>

          {/* Message */}
          <div className="bg-white rounded-lg p-4 mb-6 border-l-4 border-red-500">
            <div className="text-gray-800 leading-relaxed whitespace-pre-line">
              {message}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleEmergencyCall}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg"
            >
              <span className="text-xl">📞</span>
              <span>{callButton}</span>
            </button>
            
            <button
              onClick={handleFindHospital}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg"
            >
              <span className="text-xl">🏥</span>
              <span>{hospitalButton}</span>
            </button>
          </div>

          {/* Close Button */}
          <div className="text-center mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-sm underline transition-colors duration-200"
            >
              I understand - close this alert
            </button>
          </div>

          {/* Disclaimer */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-600">
              This is an automated alert based on symptom keywords.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmergencyAlert;