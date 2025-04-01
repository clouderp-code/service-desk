const getWebSocketUrl = () => {
  // Get the current hostname (213.210.36.2)
  const hostname = window.location.hostname;
  console.log('Current hostname:', hostname); // Debug log
  return `ws://${hostname}:8000/api/chat/ws`;
};

const getApiUrl = () => {
  const hostname = window.location.hostname;
  return `http://${hostname}:8000`;
};

export const config = {
  wsUrl: getWebSocketUrl(),
  apiUrl: getApiUrl(),
  wsRetryInterval: 3000,
  maxRetries: 5
};

// Debug log
console.log('WebSocket URL:', config.wsUrl); 