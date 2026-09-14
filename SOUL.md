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

### Track A (Retrieval)
- [ ] Initialize project directories.
- [ ] Select Vector Database and Embedding Model.
- [ ] Implement Document Loaders.
- [ ] Implement Semantic Text Splitters.
- [ ] Build Vector Store indexing pipeline.

### Track B (Generation)
- [ ] Create `mock_retriever.py` to simulate Track A.
- [ ] Design System Prompts.
- [ ] Build LangGraph state graph / LCEL chains.
- [ ] Implement Conversational Memory.
- [ ] Build Streamlit/FastAPI UI.

---

## 🎯 Next Steps
- Finalize Vector DB and LLM provider choices.
- Track A: Begin theory and implementation of Semantic Chunking.
- Track B: Begin scaffolding the LangGraph structure using the mock retriever.
