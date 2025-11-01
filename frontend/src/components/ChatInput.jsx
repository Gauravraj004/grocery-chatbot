import React, { useState } from 'react';

function ChatInput({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');

  const suggestions = [
    "Show me cheap Coke or Pepsi",
    "Find vegan bagels",
    "Subway drinks under £3",
    "Gluten-free items from ASDA"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleSuggestionClick = (suggestion) => {
    if (!disabled) {
      onSendMessage(suggestion);
    }
  };

  return (
    <div className="chat-input-container">
      <div className="suggestions">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-chip"
            onClick={() => handleSuggestionClick(suggestion)}
            disabled={disabled}
          >
            {suggestion}
          </button>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-wrapper">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask me about products... (e.g., 'show me vegan bagels')"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={disabled}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={disabled || !input.trim()}
        >
          Send 📤
        </button>
      </form>
    </div>
  );
}

export default ChatInput;
