from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from .chat_memory import ChatMemory

class QueryEngine:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        self.chat_memory = ChatMemory()
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")

    async def query(self, question: str):
        try:
            # Create the chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                memory=self.chat_memory.memory,
                return_source_documents=True,
                verbose=True
            )

            # Get response
            response = await qa_chain.acall({
                "question": question,
                "chat_history": self.chat_memory.get_chat_history()
            })

            # Extract sources
            sources = []
            for doc in response["source_documents"]:
                source = {
                    "page": doc.metadata.get("page", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content[:200] + "..."  # Preview of content
                }
                sources.append(source)

            return {
                "answer": response["answer"],
                "sources": sources
            }

        except Exception as e:
            print(f"Error in query: {e}")
            return {"error": str(e)} 