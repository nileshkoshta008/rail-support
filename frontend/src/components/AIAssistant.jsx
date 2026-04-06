import React, { useState } from 'react';
import { MessageSquare, X, Bot, Send, AlertTriangle } from 'lucide-react';
import './AIAssistant.css';

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! I am your AI Support Assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = (text) => {
    if (!text.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { type: 'user', text }]);
    setInput('');

    // Simulate AI thinking and logic branching
    setTimeout(() => {
      let botResponse = '';
      const lowerText = text.toLowerCase();
      
      if (lowerText.includes('cancel')) {
        botResponse = 'If you cancel this ticket now, a cancellation fee of ₹120 will be deducted per passenger as per Indian Railway rules for confirmed Rajdhani tickets. The remaining amount will be refunded to your original payment method in 3-5 working days. Would you like to proceed?';
      } else if (lowerText.includes('payment') || lowerText.includes('status')) {
        botResponse = 'Your Payment of ₹3,450 was SUCCESSFUL via UPI. Your ticket is currently CONFIRMED. Anything else I can assist with?';
      } else if (lowerText.includes('journey')) {
        botResponse = 'Your journey starts on 12 Oct 2026 at 16:55 PM from New Delhi (NDLS) and concludes at Mumbai Central (MMCT) the following morning. Expect a duration of 15 hours 40 minutes.';
      } else {
        botResponse = 'I am an AI assistant in training. You can ask me about ticket cancellation penalties, viewing your payment status, or checking your journey timeline.';
      }

      setMessages(prev => [...prev, { type: 'bot', text: botResponse }]);
    }, 600);
  };

  const handleQuickChip = (text) => {
    handleSend(text);
  };

  return (
    <div className="ai-assistant-wrapper">
      {!isOpen ? (
        <button className="ai-fab" onClick={() => setIsOpen(true)}>
          <Bot size={24} />
          <span className="fab-tooltip">Chat with AI Support</span>
        </button>
      ) : (
        <div className="ai-chat-window fadeIn">
          <div className="ai-header">
            <div className="ai-info">
              <Bot size={20} className="bot-icon" />
              <div>
                <h4>RailCare AI</h4>
                <span>Online</span>
              </div>
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}>
              <X size={20} />
            </button>
          </div>

          <div className="ai-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message-bubble ${msg.type}`}>
                {msg.type === 'bot' && msg.text.includes('fee') && (
                  <AlertTriangle size={16} className="alert-icon" />
                )}
                <p>{msg.text}</p>
              </div>
            ))}
          </div>

          <div className="ai-quick-chips">
            <button onClick={() => handleQuickChip('I want to cancel my ticket')}>Cancel Ticket</button>
            <button onClick={() => handleQuickChip('Check payment status')}>Payment Status</button>
            <button onClick={() => handleQuickChip('Tell me my journey timeline')}>Journey Info</button>
          </div>

          <div className="ai-input-area">
            <input 
              type="text" 
              placeholder="Type your issue..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
            />
            <button className="send-btn" onClick={() => handleSend(input)}>
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;
