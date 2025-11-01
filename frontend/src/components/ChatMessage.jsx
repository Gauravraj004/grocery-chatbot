import React from 'react';

function ChatMessage({ message }) {
  const isUser = message.type === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        {message.content}
      </div>
    </div>
  );
}

export default ChatMessage;
