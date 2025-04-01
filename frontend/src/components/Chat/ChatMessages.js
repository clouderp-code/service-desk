import React from 'react';
import Message from './components/Message';

function ChatMessages({ messages }) {
  return (
    <div className="chat-messages">
      {messages.map((msg, index) => (
        <Message key={index} message={msg} />
      ))}
    </div>
  );
}

export default ChatMessages; 