import React from "react";

const MessageBubble = ({ message, language }) => {
  const isUser = message.sender === "user";
  const isArogya = message.sender === "dr_arogya";

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-2`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'ml-2' : 'mr-2'
        }`}>
          {isUser ? (
            <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">You</span>
            </div>
          ) : (
            <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">🩺</span>
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          {/* Sender Name */}
          <div className={`text-xs text-gray-500 mb-1 ${isUser ? 'mr-1' : 'ml-1'}`}>
            {isUser ? 'You' : 'Dr. Arogya'}
            <span className="ml-2 text-gray-400">
              {formatTime(message.timestamp)}
            </span>
          </div>

          {/* Message Bubble */}
          <div
            className={`
              px-4 py-3 rounded-2xl max-w-full
              ${isUser
                ? 'bg-indigo-600 text-white rounded-tr-md'
                : 'bg-gray-100 text-gray-800 rounded-tl-md'
              }
            `}
          >
            {/* Special formatting for Dr. Arogya messages */}
            {isArogya ? (
              <div className="space-y-2">
                {message.content.split('\n').map((line, index) => {
                  // Handle numbered lists
                  if (line.match(/^\d+\./)) {
                    return (
                      <div key={index} className="flex items-start space-x-2">
                        <span className="font-semibold text-indigo-600 text-sm">
                          {line.split('.')[0]}.
                        </span>
                        <span className="text-sm">
                          {line.substring(line.indexOf('.') + 1).trim()}
                        </span>
                      </div>
                    );
                  }
                  
                  // Handle bullet points
                  if (line.startsWith('•') || line.startsWith('-')) {
                    return (
                      <div key={index} className="flex items-start space-x-2">
                        <span className="text-indigo-500 font-bold">•</span>
                        <span className="text-sm">
                          {line.substring(1).trim()}
                        </span>
                      </div>
                    );
                  }
                  
                  // Handle emoji headers
                  if (line.match(/^[🩺💊⚠️🥗🌤️🆘ℹ️🌿💬]/)) {
                    return (
                      <div key={index} className="font-semibold text-gray-800 border-b border-gray-200 pb-1 mb-2">
                        {line}
                      </div>
                    );
                  }
                  
                  // Regular lines
                  if (line.trim()) {
                    return (
                      <div key={index} className="text-sm leading-relaxed">
                        {line}
                      </div>
                    );
                  }
                  
                  return <div key={index} className="h-2"></div>;
                })}
              </div>
            ) : (
              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content}
              </div>
            )}
          </div>

          {/* Message Status */}
          {isUser && (
            <div className="text-xs text-gray-400 mt-1 mr-1">
              Delivered
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;