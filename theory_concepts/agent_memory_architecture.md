# Theory Note: Multi-Agent Cognitive Memory Architecture

## 1. The Memory Problem in Autonomous Agents
LLMs are stateless functions: `f(Prompt) -> Completion`. 
When building multi-agent systems, passing full conversational history causes:
- **Context Bloat:** Quadratic token consumption and latency.
- **Context Dilution:** Critical constraints buried in raw logs are ignored by the attention mechanism.
- **Inter-Session Amnesia:** Agents cannot reuse past workflows or learn from past debugging cycles.

## 2. The Four Cognitive Memory Tiers
1. **Working Memory:** High-frequency, volatile scratchpad for active sub-tasks.
2. **Episodic Memory:** Chronological narrative of past actions and tool executions.
3. **Semantic Memory:** Deduplicated, entity-centric facts (e.g., schemas, data distributions, domain rules).
4. **Procedural Memory:** Compiled code recipes, debugging fixes, and operational instructions.

## 3. Retrieval Strategy: Hybrid Search
Pure vector search fails on technical codebases because embedding models struggle with exact token matches (e.g., column names like `df['id_num_2']`).
A robust agent memory layer combines:
- **Lexical Search (BM25):** Strict term frequency / inverse document frequency for exact identifiers.
- **Dense Vector Search:** Cosine similarity on embeddings for conceptual similarity.
- **Graph Traversal:** Relational mapping linking entities, files, and outputs.

## 4. Architectural Role in ADEP
- Acts as the shared "Blackboard" between the Orchestrator, Explorer, Engineer, Modeler, and Storyteller.
- Decouples LLM inference from execution state.
- Reduces token overhead by ~90% via structured observation compression.
