import os
import json
import time
from datetime import datetime

from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.program import LLMTextCompletionProgram

# ייבוא מהקבצים שיצרנו
from config import TARGET_DIR, TOOLS_CONFIG, get_pinecone_index
from schemas import ExtractedItems, SourceInfo

def load_documents():
    print("📥 מתחיל טעינת מסמכים...")
    all_documents = []
    
    for tool_name, folder_name in TOOLS_CONFIG.items():
        folder_path = os.path.join(TARGET_DIR, folder_name)
        
        if os.path.exists(folder_path):
            reader = SimpleDirectoryReader(
                input_dir=folder_path, 
                required_exts=[".md"], 
                recursive=True,
                exclude_hidden=False
            )
            docs = reader.load_data()

            for doc in docs:
                doc.metadata["tool_name"] = tool_name
                
            all_documents.extend(docs)
            print(f"נטענו {len(docs)} מסמכים מתוך {tool_name}.")
        else:
            print(f"⚠️ תיקייה לא נמצאה עבור {tool_name}: {folder_path}")
            
    return all_documents

def index_documents(documents):
    print("🗂️ מתחיל אינדוקס ל-Pinecone...")
    pinecone_index = get_pinecone_index()
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    pipeline = IngestionPipeline(
        transformations=[
            MarkdownNodeParser(),
            Settings.embed_model,
        ],
        vector_store=vector_store
    )

    nodes = pipeline.run(documents=documents)
    print(f"✅ הצלחה! עובדו ואונדקסו {len(nodes)} מקטעים (chunks) ל-Pinecone.")
    return nodes

def extract_structured_data(nodes):
    print(f"📊 מתחיל חילוץ נתונים מובנים מ-{len(nodes)} מקטעים...")
    
    extraction_program = LLMTextCompletionProgram.from_defaults(
        output_cls=ExtractedItems,
        llm=Settings.llm,
        prompt_template_str=(
            "Please extract the following information from the text.\n"
            "If a specific type of information is not present, leave its list empty.\n"
            "Text: {text}"
        ),
    )
    
    all_extracted = {"items": {"decisions": [], "rules": [], "warnings": []}}
    
    for i, node in enumerate(nodes):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                extracted_data = extraction_program(text=node.text)
                
                tool_name = node.metadata.get("tool_name", "unknown")
                file_path = node.metadata.get("file_path", "unknown")
                current_time = datetime.now().isoformat()
                
                for decision in extracted_data.decisions:
                    decision.source = SourceInfo(tool=tool_name, file=file_path)
                    decision.observed_at = current_time
                    all_extracted["items"]["decisions"].append(decision.model_dump())
                    
                for rule in extracted_data.rules:
                    rule.source = SourceInfo(tool=tool_name, file=file_path)
                    rule.observed_at = current_time
                    all_extracted["items"]["rules"].append(rule.model_dump())
                    
                for warning in extracted_data.warnings:
                    warning.source = SourceInfo(tool=tool_name, file=file_path)
                    warning.observed_at = current_time
                    all_extracted["items"]["warnings"].append(warning.model_dump())
                    
                print(f"עובד מקטע {i+1}/{len(nodes)} בהצלחה.")
                break 
                
            except Exception as e:
                print(f"ניסיון {attempt + 1} נכשל עבור מקטע {i+1}:{e}")
                      
                
                if attempt < max_retries - 1:
                    print("ממתין 5 שניות לפני ניסיון נוסף...")
                    time.sleep(5)
                else:
                    print(f"מדלג על מקטע {i+1} לאחר {max_retries} ניסיונות כושלים.")
                        
                # שמירה לקובץ
                with open("extracted_knowledge.json", "w", encoding="utf-8") as f:
                    json.dump(all_extracted, f, ensure_ascii=False, indent=2)
                    
                print("✅ תהליך החילוץ הושלם. הנתונים נשמרו ל-extracted_knowledge.json")
            
            if __name__ == "__main__":
                docs = load_documents()
                if docs:
                    processed_nodes = index_documents(docs)
                    extract_structured_data(processed_nodes)
                else:
                    print("❌ לא נמצאו מסמכים לעיבוד.")
            