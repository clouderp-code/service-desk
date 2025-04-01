import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import KnowledgeBase from './components/KnowledgeBase';
import Email from './components/Email';
import Tickets from './components/Tickets';
import './App.css';

function App() {
  const [activeComponent, setActiveComponent] = useState('chat');

  const renderComponent = () => {
    switch (activeComponent) {
      case 'chat':
        return <Chat />;
      case 'knowledge':
        return <KnowledgeBase />;
      case 'email':
        return <Email />;
      case 'tickets':
        return <Tickets />;
      default:
        return <Chat />;
    }
  };

  return (
    <div className="app">
      <Sidebar 
        activeComponent={activeComponent} 
        setActiveComponent={setActiveComponent} 
      />
      <main className="main-content">
        {renderComponent()}
      </main>
    </div>
  );
}

export default App; 