import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FeedbackForm = ({ sessionId, language, onClose }) => {
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState("");
  const [helpfulAspects, setHelpfulAspects] = useState([]);
  const [improvementSuggestions, setImprovementSuggestions] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const isHindi = language?.code === "hindi";

  const helpfulOptions = isHindi ? [
    "स्पष्ट और समझने योग्य जानकारी",
    "दादी माँ के नुस्खे",
    "चेतावनी के संकेत",
    "आहार की सलाह",
    "जीवनशैली के सुझाव",
    "PDF रिपोर्ट",
    "डॉक्टर के लिए तैयारी",
    "आपातकालीन पहचान"
  ] : [
    "Clear and understandable information",
    "Traditional remedies (दादी माँ के नुस्खे)",
    "Warning signs identification",
    "Dietary recommendations",
    "Lifestyle suggestions", 
    "PDF report generation",
    "Doctor visit preparation",
    "Emergency detection"
  ];

  const handleHelpfulAspectToggle = (aspect) => {
    setHelpfulAspects(prev => 
      prev.includes(aspect)
        ? prev.filter(item => item !== aspect)
        : [...prev, aspect]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (rating === 0) {
      setError(isHindi ? "कृपया रेटिंग दें" : "Please provide a rating");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await axios.post(`${API}/sessions/${sessionId}/feedback`, {
        rating,
        comments: comments.trim() || null,
        helpful_aspects: helpfulAspects.length > 0 ? helpfulAspects : null,
        improvement_suggestions: improvementSuggestions.trim() || null
      });

      if (response.data.success) {
        setSubmitted(true);
        setTimeout(() => {
          onClose();
        }, 2000);
      }
    } catch (err) {
      setError(isHindi ? "फीडबैक भेजने में त्रुटि" : "Error submitting feedback");
      console.error("Feedback submission error:", err);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center">
          <div className="text-6xl mb-4">🙏</div>
          <h3 className="text-2xl font-bold text-green-600 mb-2">
            {isHindi ? "धन्यवाद!" : "Thank You!"}
          </h3>
          <p className="text-gray-600">
            {isHindi 
              ? "आपका फीडबैक हमें बेहतर बनाने में मदद करेगा।"
              : "Your feedback helps us improve Dr. Arogya."
            }
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-6 rounded-t-2xl">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-2xl font-bold mb-2">
                {isHindi ? "आपका फीडबैक" : "Your Feedback"}
              </h3>
              <p className="text-purple-100">
                {isHindi 
                  ? "हमें बताएं कि आपका अनुभव कैसा रहा"
                  : "Tell us about your experience with Dr. Arogya"
                }
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Form Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Rating Section */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">
              {isHindi ? "कुल मिलाकर, आप कितने संतुष्ट हैं?" : "Overall, how satisfied are you?"}
            </label>
            <div className="flex justify-center space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`text-4xl transition-all duration-200 hover:scale-110 ${
                    star <= rating 
                      ? 'text-yellow-400 drop-shadow-lg' 
                      : 'text-gray-300 hover:text-yellow-200'
                  }`}
                >
                  ⭐
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p className="text-center mt-2 text-gray-600">
                {rating === 1 && (isHindi ? "बहुत असंतुष्ट" : "Very Dissatisfied")}
                {rating === 2 && (isHindi ? "असंतुष्ट" : "Dissatisfied")}
                {rating === 3 && (isHindi ? "सामान्य" : "Neutral")}
                {rating === 4 && (isHindi ? "संतुष्ट" : "Satisfied")}
                {rating === 5 && (isHindi ? "बहुत संतुष्ट" : "Very Satisfied")}
              </p>
            )}
          </div>

          {/* Helpful Aspects */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">
              {isHindi ? "कौन से पहलू सबसे मददगार थे?" : "Which aspects were most helpful?"}
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {helpfulOptions.map((option, index) => (
                <label key={index} className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={helpfulAspects.includes(option)}
                    onChange={() => handleHelpfulAspectToggle(option)}
                    className="mt-1 h-4 w-4 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <span className="text-gray-700 text-sm">{option}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Comments */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">
              {isHindi ? "अतिरिक्त टिप्पणियां (वैकल्पिक)" : "Additional Comments (Optional)"}
            </label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder={
                isHindi 
                  ? "अपना अनुभव साझा करें..."
                  : "Share your experience..."
              }
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows="4"
            />
          </div>

          {/* Improvement Suggestions */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">
              {isHindi ? "सुधार के सुझाव (वैकल्पिक)" : "Suggestions for Improvement (Optional)"}
            </label>
            <textarea
              value={improvementSuggestions}
              onChange={(e) => setImprovementSuggestions(e.target.value)}
              placeholder={
                isHindi 
                  ? "हमें कैसे बेहतर बनाया जा सकता है..."
                  : "How can we improve..."
              }
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows="3"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors duration-200"
            >
              {isHindi ? "रद्द करें" : "Cancel"}
            </button>
            <button
              type="submit"
              disabled={submitting || rating === 0}
              className={`
                px-8 py-3 rounded-lg font-semibold transition-all duration-200
                ${submitting || rating === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700 shadow-lg hover:shadow-xl'
                }
              `}
            >
              {submitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>{isHindi ? "भेजा जा रहा है..." : "Submitting..."}</span>
                </div>
              ) : (
                isHindi ? "फीडबैक भेजें" : "Submit Feedback"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackForm;