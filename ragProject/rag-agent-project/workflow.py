import json
import os
from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Event
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.llms import ChatMessage
from llama_index.core import Settings, PromptTemplate

from schemas import StructuredSearchParams

from datetime import datetime, timedelta


# ==========================================
# Events Definition
# ==========================================
class InputValidatedEvent(Event):
    query: str
    chat_history: list

class RetrieveEvent(Event):
    query: str
    nodes: list

class FallbackSearchEvent(Event):
    query: str
    chat_history: list

class SemanticSearchEvent(Event):
    query: str
    chat_history: list

class StructuredSearchEvent(Event):
    query: str
    chat_history: list

# ==========================================
# Helper Functions
# ==========================================
def execute_structured_search(entity_type: str, keyword: str = "", days_back: int = 0) -> str:
    try:
        file_path = os.path.abspath("extracted_knowledge.json")
        if not os.path.exists(file_path):
             return f"שגיאה: קובץ נתונים מובנים לא נמצא."
             
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        items = data.get("items", {}).get(entity_type, [])
        
        # --- תחילת לוגיקת הסינון ---
        filtered_items = []
        
        # חישוב תאריך החיתוך אם התבקש סינון לפי זמן
        cutoff_date = None
        if days_back > 0:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
        for item in items:
            # 1. סינון לפי מילת מפתח (אם קיימת)
            if keyword and keyword.strip():
                # הופכים את כל האובייקט לטקסט ומחפשים בו את מילת המפתח (לא רגיש לאותיות רישיות)
                if keyword.lower() not in str(item).lower():
                    continue # מדלגים על הפריט אם המילה לא נמצאה
                    
            # 2. סינון לפי תאריך (אם נדרש)
            if cutoff_date:
                observed_str = item.get("observed_at", "")
                if observed_str:
                    try:
                        item_date = datetime.fromisoformat(observed_str)
                        if item_date < cutoff_date:
                            continue # מדלגים אם הפריט ישן מדי
                    except ValueError:
                        pass # במקרה של שגיאת תאריך, נשאיר את הפריט
                        
            # אם הפריט עבר את כל הסינונים, נוסיף אותו לרשימה הסופית
            filtered_items.append(item)
        # --- סוף לוגיקת הסינון ---

        if not filtered_items:
            return f"לא נמצאו נתונים מסוג {entity_type} התואמים לסינון המבוקש."
            
        return json.dumps(filtered_items, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"שגיאה בשליפת נתונים: {str(e)}"

# ==========================================
# Workflow Definition
# ==========================================
class RAGWorkflow(Workflow):
    def __init__(self, rag_index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rag_index = rag_index

    @step
    async def validate_input(self, ev: StartEvent) -> InputValidatedEvent | StopEvent:
        query = ev.get("query")
        chat_history = ev.get("chat_history", [])
        
        if not query or len(query.strip()) < 3:
            return StopEvent(result="❌ שגיאה: השאלה קצרה מדי. אנא נסחי שאלה ברורה.")

        if chat_history:
            print("📝 משכתב את השאלה בהתבסס על היסטוריית השיחה...")
            recent_history = chat_history[-3:]
            history_lines = []
            for item in recent_history:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    history_lines.append(f"Q: {item[0]}\nA: {item[1]}")
                elif isinstance(item, dict):
                    history_lines.append(f"{item.get('role', 'msg')}: {item.get('content', '')}")
                else:
                    try:
                        history_lines.append(f"{item.role}: {item.content}")
                    except:
                        history_lines.append(str(item))
            
            history_str = "\n".join(history_lines)
            
            rewrite_prompt = (
                "Rewrite the current question so it is clear and completely standalone, "
                "using context from the conversation history.\n"
                f"History:\n{history_str}\n\n"
                f"Current question: {query}\n"
                "Standalone question:"
            )
            
            response = await Settings.llm.achat([ChatMessage(role="user", content=rewrite_prompt)])
            query = str(response.message.content).strip()
            print(f"✨ השאלה שוכתבה ל: {query}")
           
        return InputValidatedEvent(query=query, chat_history=chat_history)

    @step
    async def route_query(self, ev: InputValidatedEvent) -> SemanticSearchEvent | StructuredSearchEvent:
        prompt = (
            "Classify the following user query into exactly one of these two categories:\n"
            "1. 'structured' - if the user asks for a list of items (decisions, rules, warnings), recent updates, or filtering.\n"
            "2. 'semantic' - if the user asks conceptual questions (how to, why, explanations).\n"
            "Respond with ONLY ONE WORD: 'structured' or 'semantic'.\n"
            f"Query: {ev.query}"
        )
        
        response = await Settings.llm.achat([ChatMessage(role="user", content=prompt)])
        decision = str(response.message.content).strip().lower()
        
        print(f"🔀 החלטת ניתוב: {decision}")
        
        if "structured" in decision:
            return StructuredSearchEvent(query=ev.query, chat_history=ev.chat_history)
        else:
            return SemanticSearchEvent(query=ev.query, chat_history=ev.chat_history)
    
    @step
    async def retrieve_data(self, ev: SemanticSearchEvent) -> RetrieveEvent | FallbackSearchEvent | StopEvent:
        retriever = self.rag_index.as_retriever(similarity_top_k=6)
        nodes = await retriever.aretrieve(ev.query)
        
        if not nodes:
            return StopEvent(result="לא מצאתי מידע רלוונטי במסמכי התיעוד לשאלה זו.")
            
        processor = SimilarityPostprocessor(similarity_cutoff=0.5)
        high_quality_nodes = processor.postprocess_nodes(nodes)
        
        if not high_quality_nodes:
            return FallbackSearchEvent(query=ev.query, chat_history=ev.chat_history)
            
        return RetrieveEvent(query=ev.query, nodes=high_quality_nodes)

    @step
    async def fallback_search(self, ev: FallbackSearchEvent) -> RetrieveEvent | StopEvent:
        print("🔄 מפעיל חיפוש מורחב (Fallback)...")
        retriever = self.rag_index.as_retriever(similarity_top_k=10)
        nodes = await retriever.aretrieve(ev.query)
        
        if not nodes:
            return StopEvent(result="לא מצאתי מידע גם לאחר חיפוש מורחב. ייתכן שנדרש הקשר נוסף לשאלה.")
            
        return RetrieveEvent(query=ev.query, nodes=nodes)

    @step
    async def synthesize_response(self, ev: RetrieveEvent) -> StopEvent:
        print("✍️ מנסח תשובה סופית (Synthesizing)...")
        docs_text = "\n\n".join([node.text for node in ev.nodes])
        
        prompt_text = (
            f"Answer the following question based ONLY on the provided context.\n"
            f"Your final answer MUST be in fluent Hebrew.\n\n"
            f"Context:\n{docs_text}\n\n"
            f"Question: {ev.query}"
        )
        
        try:
            res = await Settings.llm.achat([ChatMessage(role="user", content=prompt_text)])
            ans = str(res.message.content)
            
            srcs = list(set([n.metadata.get('tool_name', 'Unknown') for n in ev.nodes]))
            return StopEvent(result=ans + f"\n\n*מקורות: {', '.join(srcs)}*")
            
        except Exception as err:
            return StopEvent(result=f"❌ שגיאה בניסוח: {str(err)}")

    @step
    async def structured_search_step(self, ev: StructuredSearchEvent) -> StopEvent:
        print("📊 מפעיל חיפוש מובנה (Structured Outputs)...")
        
        try:
            # 1. יצירת אובייקט PromptTemplate תקני במקום מחרוזת רגילה
            extraction_prompt = PromptTemplate(
                "Extract search parameters from the user query: {query_str}\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. If the user asks for a general list (e.g., 'all decisions', 'list rules') WITHOUT specifying a topic, you MUST set 'keyword' to an empty string ''.\n"
                "2. ONLY set a 'keyword' if the user explicitly asks for a specific topic (e.g., 'rules about database').")

            # 2. העברת האובייקט והמשתנים למודל
            search_params = await Settings.llm.astructured_predict(
                StructuredSearchParams,
                prompt=extraction_prompt,
                query_str=ev.query
            )
            
            print(f"DEBUG - Extracted Params: {search_params.model_dump()}")
            
            # תיקון אוטומטי של טעויות נפוצות
            entity = search_params.entity_type.lower()
            if "rule" in entity: entity = "rules"
            elif "warn" in entity: entity = "warnings"
            else: entity = "decisions"

            raw_data = execute_structured_search(
                entity_type=entity,
                keyword=search_params.keyword,
                days_back=search_params.days_back
            )
          
            synthesis_prompt = (
                "You are a strict data reporter. \n"
                "I am giving you raw JSON data that contains the EXACT items the user asked for.\n"
                "You MUST output this data to the user in fluent Hebrew.\n"
                "List every single item from the data below clearly.\n\n"
                f"Data:\n{raw_data}\n\n"
                f"User Query: {ev.query}"
            )

            final_res = await Settings.llm.achat([ChatMessage(role="user", content=synthesis_prompt)])
            return StopEvent(result=str(final_res.message.content) + "\n\n*מקור: מאגר מובנה*")
            
        except Exception as err:
            return StopEvent(result=f"❌ שגיאה כללית בחיפוש המובנה: {str(err)}")





            
            
