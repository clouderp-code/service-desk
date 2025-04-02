import React from 'react';

function Message({ message }) {
  if (!message.sources) {
    return (
      <div className={`message-wrapper ${message.isUser ? 'user' : 'assistant'}`}>
        <div className="message">
          <div className="message-content">{message.text}</div>
          <div className="message-timestamp">{message.timestamp}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`message-wrapper ${message.isUser ? 'user' : 'assistant'}`}>
      <div className="message">
        <div className="message-content">{message.answer}</div>
        <div className="message-sources">
          <h4>Sources:</h4>
          {message.sources.map((source, index) => (
            <div key={index} className="source-item">
              <div className="source-header">
                Page {source.page} from {source.source}
              </div>
              <div className="source-preview">{source.content}</div>
            </div>
          ))}
        </div>
        <div className="message-timestamp">{message.timestamp}</div>
      </div>
    </div>
  );
}

export default Message; 