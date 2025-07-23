import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LanguageSelector = ({ onLanguageSelect }) => {
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API}/languages`);
      if (response.data.success) {
        setLanguages(response.data.data);
      }
    } catch (err) {
      setError("Failed to load languages");
      console.error("Error fetching languages:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageSelect = async (language) => {
    setCreating(true);
    setError(null);

    try {
      // Create session
      const sessionResponse = await axios.post(`${API}/sessions`, {
        language: language.code
      });

      if (sessionResponse.data.success) {
        const sessionId = sessionResponse.data.data.id;
        
        // Set language for session
        const languageResponse = await axios.post(
          `${API}/sessions/${sessionId}/language`,
          {
            session_id: sessionId,
            selected_language: language.code
          }
        );

        if (languageResponse.data.success) {
          onLanguageSelect(sessionId, language);
        }
      }
    } catch (err) {
      setError("Failed to start session. Please try again.");
      console.error("Error creating session:", err);
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        {/* Welcome Message */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            Welcome to Dr. Arogya! 🙏
          </h2>
          <p className="text-gray-600 text-lg mb-2">
            I can speak in your preferred language.
          </p>
          <p className="text-gray-500">
            Please select one to continue:
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Language Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
          {languages.map((language, index) => (
            <button
              key={language.code}
              onClick={() => handleLanguageSelect(language)}
              disabled={creating}
              className={`
                p-6 rounded-xl border-2 transition-all duration-200 text-left
                hover:border-indigo-400 hover:shadow-lg hover:scale-105
                focus:outline-none focus:ring-4 focus:ring-indigo-200
                ${creating ? 'opacity-50 cursor-not-allowed' : 'hover:bg-indigo-50'}
                ${index < 4 ? 'border-indigo-200 bg-gradient-to-r from-indigo-50 to-blue-50' : 'border-gray-200 bg-white'}
              `}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">
                  {index === 0 && "🌍"}
                  {index === 1 && "🇮🇳"}
                  {index === 2 && "🗣️"}
                  {index === 3 && "💬"}
                  {index > 3 && "🌐"}
                </span>
                <span className="text-sm text-gray-500 font-mono">
                  {index + 1}
                </span>
              </div>
              
              <h3 className="font-bold text-lg text-gray-800 mb-1">
                {language.native_name}
              </h3>
              <p className="text-sm text-gray-600">
                {language.name}
              </p>
            </button>
          ))}
        </div>

        {/* Loading State */}
        {creating && (
          <div className="text-center mt-8">
            <div className="inline-flex items-center space-x-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
              <span className="text-gray-600">Starting your consultation...</span>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="bg-blue-50 rounded-lg p-6">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
              <span className="mr-2">ℹ️</span>
              How it works:
            </h4>
            <ol className="space-y-2 text-blue-800">
              <li className="flex items-start">
                <span className="inline-block w-6 h-6 bg-blue-200 rounded-full text-xs text-center leading-6 mr-3 font-semibold">1</span>
                Select your preferred language
              </li>
              <li className="flex items-start">
                <span className="inline-block w-6 h-6 bg-blue-200 rounded-full text-xs text-center leading-6 mr-3 font-semibold">2</span>
                Tell me about your health concerns
              </li>
              <li className="flex items-start">
                <span className="inline-block w-6 h-6 bg-blue-200 rounded-full text-xs text-center leading-6 mr-3 font-semibold">3</span>
                Receive a complete health guide with traditional remedies
              </li>
              <li className="flex items-start">
                <span className="inline-block w-6 h-6 bg-blue-200 rounded-full text-xs text-center leading-6 mr-3 font-semibold">4</span>
                Download PDF report for your doctor visit
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageSelector;