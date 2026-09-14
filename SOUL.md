# Project Soul: LangChain RAG Pipeline

## 🏗️ Core Architecture & Agent Sync
This document serves as the central memory system for human-agent collaboration. It synchronizes state between Allen's Agent (Antigravity) and Divya's Agent.

### Work Division
* **Track A (Allen & Antigravity):** Data Ingestion, Semantic Chunking, Embeddings, Vector Store, and Retriever interface.
* **Track B (Divya & Agent):** LangChain/LangGraph orchestration, Memory, Prompts, and User Interface.

---

## 📜 Integration Contracts (The API)
To allow concurrent development, Track B can safely assume Track A will provide the following interface once complete. Divya's agent should build the LangGraph using a mock of this interface.

**Retriever Output Schema:**
```python
from langchain_core.documents import Document
from typing import List

class RAGRetriever:
    def get_relevant_chunks(self, query: str) -> List[Document]:
        """
        Takes a user query string and returns a list of the most semantically relevant 
        LangChain Document objects containing the chunked text and metadata.
        """
        pass
```

---

## 📈 Current Progress

### Track A (Retrieval & Infrastructure)
- [x] Initialize project context graph (Graft integrated).
- [x] Set up `agentmemory` persistent memory server & cognitive skills.
- [ ] Select Vector Database and Embedding Model.
- [ ] Implement Document Loaders.
- [ ] Implement Semantic Text Splitters.
- [ ] Build Vector Store indexing pipeline.

### Track B (Generation & Orchestration)
- [ ] Create `mock_retriever.py` to simulate Track A.
- [ ] Design System Prompts for specialized fleet agents.
- [ ] Build LangGraph state graph / LCEL chains.
- [ ] Connect LangGraph agents to `agentmemory` REST API.
- [ ] Build Streamlit/FastAPI UI.

---

## 🎯 Key Architectural Decisions & Next Steps
- **Context Management:** Graft initialized locally to maintain an active structural map of the codebase for developer AI agents.
- **Shared Memory Layer:** `rohitg00/agentmemory` configured and wired with 17 agent skills.
- **Next Steps:**
  1. Define Python client wrapper in `/core/memory.py` to interact with `agentmemory` REST API (:3111).
  2. Implement semantic chunking strategy and embedding model selection for the RAG retriever pipeline.
