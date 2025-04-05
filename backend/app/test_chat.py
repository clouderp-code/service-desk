import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_chat():
    uri = "ws://localhost:8000/api/chat/ws"
    async with websockets.connect(uri) as websocket:
        # Test questions about your PDF content
        questions = [
            "What types of products do you offer?",
            "How fresh are your products?",
            "Are your products organic?",
            "What farming methods do you use?",
            "How do you ensure soil fertility?"
        ]
        
        for question in questions:
            logger.info(f"\n=== Testing Question: {question} ===")
            
            message = {
                "message": question
            }
            
            # Send question
            logger.info(f"Sending: {json.dumps(message, indent=2)}")
            await websocket.send(json.dumps(message))
            
            # Get response
            response = await websocket.recv()
            response_data = json.loads(response)
            
            # Print response
            logger.info("Received Response:")
            if response_data.get("error"):
                logger.error(f"Error: {response_data['error']}")
            else:
                logger.info(f"Answer: {response_data['response']}")
            
            # Wait between questions
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(test_chat())
    except Exception as e:
        logger.error(f"Error: {str(e)}") 