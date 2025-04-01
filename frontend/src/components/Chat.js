const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

ws.onopen = () => {
  console.log('Connected to chat server');
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.error) {
    console.error('Error:', response.error);
  } else {
    console.log('Response:', response.response);
    // Handle the response (update UI, etc.)
  }
};

// Function to send messages
const sendMessage = (content) => {
  ws.send(JSON.stringify({ content }));
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from chat server');
}; 