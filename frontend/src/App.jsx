import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import ChatMessage from './components/ChatMessage';
import ProductCard from './components/ProductCard';
import ChatInput from './components/ChatInput';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message
    setMessages([
      {
        type: 'bot',
        content: "👋 Hi! I'm your grocery shopping assistant. I can help you find products and compare prices across different shops.",
        timestamp: new Date()
      }
    ]);
  }, []);

  const handleSendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;

    // Add user message
    const userMsg = {
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: userMessage
      });

      const botResponse = response.data;

      // Add bot message with products
      const botMsg = {
        type: 'bot',
        content: botResponse.message,
        products: botResponse.products || [],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error('Error:', error);
      const errorMsg = {
        type: 'bot',
        content: '❌ Sorry, I encountered an error. Please make sure the backend server is running on port 5000.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await axios.post('http://localhost:5000/api/reset');
      setMessages([
        {
          type: 'bot',
          content: "🔄 Conversation reset! How can I help you with your grocery shopping?",
          timestamp: new Date()
        }
      ]);
    } catch (error) {
      console.error('Error resetting:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🛒 Grocery Shopping Assistant</h1>
          <button className="reset-button" onClick={handleReset} title="Reset conversation">
            🔄 Reset
          </button>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index}>
              <ChatMessage message={message} />
              {message.products && message.products.length > 0 && (
                <div className="products-grid">
                  {message.products.map((product, pIndex) => (
                    <ProductCard key={pIndex} product={product} />
                  ))}
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="message bot-message">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

export default App;
