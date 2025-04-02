from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

class ChatMemory:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def add_user_message(self, message: str):
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str):
        self.memory.chat_memory.add_ai_message(message)

    def get_chat_history(self):
        return self.memory.chat_memory.messages

    def clear(self):
        self.memory.clear() 