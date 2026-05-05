import gradio as gr
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore

# ייבוא מהקבצים שיצרנו
from config import get_pinecone_index
from workflow import RAGWorkflow

print("🚀 מאתחל את המערכת...")

# חיבור לאינדקס הקיים ב-Pinecone (שנוצר/עודכן על ידי ingestion.py)
pinecone_index = get_pinecone_index()
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# אתחול ה-Workflow
workflow = RAGWorkflow(rag_index=index, timeout=180.0)

async def chat_with_workflow(message, history):
    try:
        result = await workflow.run(query=message, chat_history=history)
        return str(result)
    except Exception as e:
        return f"❌ שגיאה בתשאול: {str(e)}"

print("🌐 מפעיל ממשק Gradio...")

demo = gr.ChatInterface(
    fn=chat_with_workflow,
    title="🤖 Agentic Docs RAG (Event-Driven)",
    description="שאל אותי שאלות על החלטות הפיתוח, חוקי המערכת והארכיטקטורה מתוך קבצי התיעוד."
)

if __name__ == "__main__":
    demo.launch()
