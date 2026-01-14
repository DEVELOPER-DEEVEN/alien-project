# The Learning Core (RAG)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Type: RAG](https://img.shields.io/badge/Architecture-RAG-purple.svg)]()

**Architect: Deeven Seru**

---

## 📑 Table of Contents

1.  [Concept](#concept)
2.  [Vector Database Architecture](#vector-database-architecture)
3.  [Retrieval Logic](#retrieval-logic)
4.  [Teaching the Agent](#teaching-the-agent)

---

## 1. Concept

Standard LLMs have a fixed knowledge cutoff and do not know how *your* specific custom software works. The `learner/` module solves this via **Retrieval-Augmented Generation (RAG)**.

When the agent attempts to use "Photoshop", it queries the learner module: *"How do I remove the background in Photoshop 2024?"*. The module retrieves relevant snippets from:
1.  **Docs**: Official manuals indexed by the user.
2.  **Experiences**: Successful past executions of the same task.

---

## 2. Vector Database Architecture

We utilize a high-performance vector store (ChromaDB or FAISS) to index knowledge.

### Schema
Documents are chunked and embedded into high-dimensional space.

| Field | Description |
| :--- | :--- |
| `id` | Unique UUID. |
| `content` | The raw text chunk (e.g., "Click Select > Subject to mask..."). |
| `embedding` | 1536-dim vector (OpenAI `text-embedding-3-small`). |
| `metadata` | Source info (`{"app": "Photoshop", "type": "manual"}`). |

---

## 3. Retrieval Logic

The retrieval process follows a **Hybrid Search** strategy:

1.  **Semantic Search**: Finds conceptually similar documents using Cosine Similarity.
2.  **Keyword Filtering**: Filters results to the current active application. You don't want "Excel" help when working in "Word".

```mermaid
graph TD
    Query[User Query] --> Embedding[Embedding Model]
    Embedding --> Vector[Vector Search]
    Vector --> Filter[Metadata Filter (App Name)]
    Filter --> Context[Final Context Window]
```

---

## 4. Teaching the Agent

You can actively improve the agent's performance by adding documents.

**Procedure:**
1.  Place markdown or text files in `alien/learner/documents/`.
2.  Run the indexer:
    ```bash
    python -m alien.learner.indexer --dir alien/learner/documents/
    ```
3.  The system will parse, chunk, and embed the files. The next time the agent runs, it will have access to this new knowledge.

---
*© 2026 Deeven Seru. All Rights Reserved.*
