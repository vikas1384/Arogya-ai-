import React, { useState } from "react";
import axios from "axios";
import FeedbackForm from "./FeedbackForm";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HealthGuide = ({ healthGuide, sessionId, language }) => {
  const [showFeedback, setShowFeedback] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const handleDownloadPDF = async (includeChatHistory = false) => {
    setPdfLoading(true);
    setPdfError(null);

    try {
      const response = await axios.post(`${API}/sessions/${sessionId}/generate-pdf`, {
        session_id: sessionId,
        include_chat_history: includeChatHistory
      });

      if (response.data.pdf_url) {
        // Create download link
        const link = document.createElement('a');
        link.href = `${BACKEND_URL}${response.data.pdf_url}`;
        link.download = response.data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      setPdfError("Failed to generate PDF. Please try again.");
      console.error("PDF generation error:", err);
    } finally {
      setPdfLoading(false);
    }
  };

  const isHindi = language?.code === "hindi";

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-t-2xl text-white p-6">
        <div className="flex items-center justify-center mb-4">
          <div className="text-4xl mr-3">🩺</div>
          <div>
            <h2 className="text-3xl font-bold">
              {isHindi ? "आपकी स्वास्थ्य गाइड" : "Your Health Guide"}
            </h2>
            <p className="text-blue-100">
              {isHindi ? "डॉ. आरोग्य द्वारा तैयार" : "Prepared by Dr. Arogya"}
            </p>
          </div>
        </div>
        
        <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
          <p className="text-sm">
            {isHindi 
              ? "यह गाइड आपको डॉक्टर के पास जाने के लिए तैयार करने में मदद करेगा"
              : "This guide will help you prepare for your doctor's visit"
            }
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-white shadow-xl rounded-b-2xl border border-gray-100">
        <div className="p-8 space-y-8">
          
          {/* Symptom Summary */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              🧠 <span className="ml-2">
                {isHindi ? "आपके लक्षणों की समझ" : "Understanding Your Symptoms"}
              </span>
            </h3>
            <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
              <p className="text-gray-700 leading-relaxed">
                {healthGuide.symptom_summary}
              </p>
            </div>
          </section>

          {/* Possible Conditions */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              🔍 <span className="ml-2">
                {isHindi ? "डॉक्टर के लिए संभावित जांच बिंदु" : "Potential Areas for Your Doctor to Explore"}
              </span>
            </h3>
            <div className="grid gap-3">
              {healthGuide.possible_conditions.map((condition, index) => (
                <div key={index} className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-400">
                  <div className="flex items-start">
                    <span className="text-yellow-600 mr-2">•</span>
                    <span className="text-gray-700">{condition}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* OTC Recommendations */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              💊 <span className="ml-2">
                {isHindi ? "घरेलू देखभाल के सुझाव" : "Self-Care Recommendations"}
              </span>
            </h3>
            <div className="grid gap-3">
              {healthGuide.otc_recommendations.map((recommendation, index) => (
                <div key={index} className="bg-green-50 rounded-lg p-3 border-l-4 border-green-400">
                  <div className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-700">{recommendation}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Warning Signs */}
          <section>
            <h3 className="text-xl font-bold text-red-700 mb-4 flex items-center">
              ⚠️ <span className="ml-2">
                {isHindi ? "चेतावनी के संकेत" : "Important Warning Signs"}
              </span>
            </h3>
            <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
              <p className="text-red-800 font-semibold mb-3">
                {isHindi 
                  ? "निम्नलिखित लक्षण होने पर तुरंत डॉक्टर से मिलें:"
                  : "Seek immediate medical attention if you experience:"
                }
              </p>
              <div className="space-y-2">
                {healthGuide.warning_signs.map((sign, index) => (
                  <div key={index} className="flex items-start">
                    <span className="text-red-600 mr-2 font-bold">⚠</span>
                    <span className="text-red-700">{sign}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Traditional Remedies */}
          {healthGuide.traditional_remedies.length > 0 && (
            <section>
              <h3 className="text-xl font-bold text-orange-700 mb-4 flex items-center">
                🌿 <span className="ml-2">
                  {isHindi ? "दादी माँ के नुस्खे" : "Traditional Grandmother's Remedies"}
                </span>
              </h3>
              <div className="bg-orange-50 rounded-lg p-4 border-2 border-orange-200">
                <p className="text-orange-800 text-sm mb-4 italic">
                  {isHindi 
                    ? "ये पारंपरिक उपचार पीढ़ियों से चले आ रहे हैं। ये आराम दे सकते हैं, लेकिन चिकित्सा इलाज की जगह नहीं ले सकते।"
                    : "These time-tested remedies have been passed down through generations. They may provide comfort but should complement, not replace, medical treatment."
                  }
                </p>
                
                <div className="space-y-4">
                  {healthGuide.traditional_remedies.map((remedy, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-orange-200">
                      <h4 className="font-bold text-orange-800 mb-2">{remedy.name}</h4>
                      
                      <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="font-semibold text-gray-700 mb-1">
                            {isHindi ? "सामग्री:" : "Ingredients:"}
                          </p>
                          <p className="text-gray-600 mb-2">{remedy.ingredients.join(", ")}</p>
                          
                          <p className="font-semibold text-gray-700 mb-1">
                            {isHindi ? "तैयारी:" : "Preparation:"}
                          </p>
                          <p className="text-gray-600">{remedy.preparation}</p>
                        </div>
                        
                        <div>
                          <p className="font-semibold text-gray-700 mb-1">
                            {isHindi ? "उपयोग:" : "Usage:"}
                          </p>
                          <p className="text-gray-600 mb-2">{remedy.usage}</p>
                          
                          <p className="font-semibold text-gray-700 mb-1">
                            {isHindi ? "फायदे:" : "Benefits:"}
                          </p>
                          <p className="text-gray-600">{remedy.benefits}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Dietary Advice */}
          <section>
            <h3 className="text-xl font-bold text-purple-700 mb-4 flex items-center">
              🥗 <span className="ml-2">
                {isHindi ? "आहार की सलाह" : "Dietary Recommendations"}
              </span>
            </h3>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="grid gap-3">
                {healthGuide.dietary_advice.map((advice, index) => (
                  <div key={index} className="flex items-start">
                    <span className="text-purple-600 mr-2">🍎</span>
                    <span className="text-gray-700">{advice}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Lifestyle Tips */}
          <section>
            <h3 className="text-xl font-bold text-teal-700 mb-4 flex items-center">
              🌤️ <span className="ml-2">
                {isHindi ? "जीवनशैली की सिफारिशें" : "Lifestyle Modifications"}
              </span>
            </h3>
            <div className="bg-teal-50 rounded-lg p-4">
              <div className="grid gap-3">
                {healthGuide.lifestyle_tips.map((tip, index) => (
                  <div key={index} className="flex items-start">
                    <span className="text-teal-600 mr-2">✨</span>
                    <span className="text-gray-700">{tip}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* When to See Doctor */}
          <section>
            <h3 className="text-xl font-bold text-indigo-700 mb-4 flex items-center">
              🆘 <span className="ml-2">
                {isHindi ? "डॉक्टर से कब मिलें" : "When to Seek Medical Care"}
              </span>
            </h3>
            <div className="bg-indigo-50 rounded-lg p-4 border-l-4 border-indigo-500">
              <div className="space-y-2">
                {healthGuide.when_to_see_doctor.map((guideline, index) => (
                  <div key={index} className="flex items-start">
                    <span className="text-indigo-600 mr-2">🏥</span>
                    <span className="text-gray-700">{guideline}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Action Buttons */}
          <section className="border-t border-gray-200 pt-6">
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              {/* Download PDF Buttons */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">
                  {isHindi ? "अपनी रिपोर्ट डाउनलोड करें:" : "Download Your Report:"}
                </h4>
                <div className="space-y-2">
                  <button
                    onClick={() => handleDownloadPDF(false)}
                    disabled={pdfLoading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 disabled:opacity-50"
                  >
                    <span>📄</span>
                    <span>
                      {isHindi ? "स्वास्थ्य गाइड PDF" : "Health Guide PDF"}
                    </span>
                  </button>
                  
                  <button
                    onClick={() => handleDownloadPDF(true)}
                    disabled={pdfLoading}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 disabled:opacity-50"
                  >
                    <span>📋</span>
                    <span>
                      {isHindi ? "बातचीत के साथ PDF" : "Complete Report with Chat"}
                    </span>
                  </button>
                </div>
              </div>

              {/* Feedback Button */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">
                  {isHindi ? "हमारी मदद करें:" : "Help us improve:"}
                </h4>
                <button
                  onClick={() => setShowFeedback(true)}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <span>⭐</span>
                  <span>
                    {isHindi ? "फीडबैक दें" : "Give Feedback"}
                  </span>
                </button>
              </div>
            </div>

            {pdfError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-red-600 text-sm">{pdfError}</p>
              </div>
            )}

            {pdfLoading && (
              <div className="text-center py-4">
                <div className="inline-flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">
                    {isHindi ? "PDF तैयार की जा रही है..." : "Generating PDF..."}
                  </span>
                </div>
              </div>
            )}
          </section>

          {/* Disclaimer */}
          <section className="bg-gray-50 rounded-lg p-6 border-2 border-gray-200">
            <h4 className="font-bold text-gray-800 mb-3 flex items-center">
              <span className="mr-2">⚠️</span>
              {isHindi ? "महत्वपूर्ण चिकित्सा अस्वीकरण" : "Important Medical Disclaimer"}
            </h4>
            <p className="text-gray-700 text-sm leading-relaxed">
              {isHindi ? (
                `यह रिपोर्ट डॉ. आरोग्य, एक AI स्वास्थ्य सहायक द्वारा तैयार की गई है और केवल जानकारी के उद्देश्य से है। 
                यह चिकित्सा सलाह, निदान या उपचार का विकल्प नहीं है। स्वास्थ्य संबंधी चिंताओं के लिए हमेशा योग्य 
                स्वास्थ्य पेशेवरों से सलाह लें। मेडिकल इमरजेंसी के मामले में तुरंत अपनी स्थानीय आपातकालीन सेवाओं से संपर्क करें।`
              ) : (
                `This report is generated by Dr. Arogya, an AI health assistant, and is intended for informational 
                purposes only. It does not constitute medical advice, diagnosis, or treatment. Always consult with 
                qualified healthcare professionals for medical concerns. In case of medical emergencies, contact 
                your local emergency services immediately.`
              )}
            </p>
          </section>
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedback && (
        <FeedbackForm
          sessionId={sessionId}
          language={language}
          onClose={() => setShowFeedback(false)}
        />
      )}
    </div>
  );
};

export default HealthGuide;