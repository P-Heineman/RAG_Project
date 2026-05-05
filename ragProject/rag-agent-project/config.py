import os
import ssl
import httpx
import urllib3
from dotenv import load_dotenv

from llama_index.core import Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from pinecone import Pinecone, ServerlessSpec

# ==========================================
# 1. Constants & Environment
# ==========================================
load_dotenv()

COHERE_MODEL_NAME = "embed-multilingual-v3.0"
PINECONE_INDEX_NAME = "agentic-coding-index"
EMBEDDING_DIMENSION = 1024
TARGET_DIR = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'meta-observer-target'))

TOOLS_CONFIG = {
    "Cursor": ".cursor",
    "Claude Code": ".claude"
}
# ==========================================
# 2. Network Patches (For filtered networks)
# ==========================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Patch Sync Client
if not hasattr(httpx.Client, "_is_patched"):
    original_sync_init = httpx.Client.__init__
    def patched_sync_init(self, *args, **kwargs):
        kwargs['verify'] = False
        kwargs['timeout'] = 120.0
        original_sync_init(self, *args, **kwargs)
    httpx.Client.__init__ = patched_sync_init
    httpx.Client._is_patched = True
    
# Patch Async Client
if not hasattr(httpx.AsyncClient, "_is_patched"):
    original_async_init = httpx.AsyncClient.__init__
    def patched_async_init(self, *args, **kwargs):
        kwargs['verify'] = False
        kwargs['timeout'] = httpx.Timeout(180.0, connect=60.0)
        kwargs['limits'] = httpx.Limits(max_keepalive_connections=5, max_connections=10, keepalive_expiry=30.0)
        original_async_init(self, *args, **kwargs)
    httpx.AsyncClient.__init__ = patched_async_init
    httpx.AsyncClient._is_patched = True
print("Network patches applied successfully.")

# ==========================================
# 3. LlamaIndex Global Settings
# ==========================================
Settings.embed_model = CohereEmbedding(
    model_name=COHERE_MODEL_NAME,
    api_key=os.getenv("COHERE_API_KEY"),
    timeout=120.0
)

Settings.llm = Cohere(
    model="command-r-08-2024",  
    api_key=os.getenv("COHERE_API_KEY"),
    timeout=120.0,
    max_tokens=512,
    system_prompt=(
        "You are an expert AI assistant for developers.\n"
        "The context documents are usually in English, but the user will ask questions in Hebrew.\n"
        "You must search the English context, find the relevant information, and answer the user in fluent Hebrew."
    )
)
Settings.context_window = 8192  
Settings.num_output = 512

print("LLM and Index are ready for querying.")

# ==========================================
# 4. Pinecone Initialization
# ==========================================
def get_pinecone_index():
    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY"),
        ssl_verify=False
    )

    if PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        print(f"Creating new Pinecone index: {PINECONE_INDEX_NAME}...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1") 
        )
    return pc.Index(PINECONE_INDEX_NAME)

print("Configuration loaded successfully.")