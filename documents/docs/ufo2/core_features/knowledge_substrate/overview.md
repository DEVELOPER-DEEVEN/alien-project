# Knowledge Substrate

Alien provides versatile mechanisms to enhance the AppAgent's capabilities through RAG (Retrieval-Augmented Generation) and other knowledge retrieval techniques. These mechanisms improve the AppAgent's task understanding, plan quality, and interaction efficiency with applications.

## Supported Knowledge Sources

Alien currently supports the following knowledge retrieval methods:

| Knowledge Source | Description |
|------------------|-------------|
| [Help Documents](./learning_from_help_document.md) | Retrieve knowledge from offline help documentation indexed for specific applications. |
| [Bing Search](./learning_from_bing_search.md) | Search online information via Bing to obtain up-to-date knowledge. |
| [Self-Experience](./experience_learning.md) | Learn from the agent's own successful task execution history. |
| [User Demonstrations](./learning_from_demonstration.md) | Learn from action trajectories demonstrated by users. |

## Context Provision

Alien provides knowledge to the AppAgent through the `context_provision` method defined in the `AppAgent` class:

```python
async def context_provision(
    self, request: str = "", context: Context = None
) -> None:
    """
    Provision the context for the app agent.
    :param request: The request sent to the Bing search retriever.
    """

    Alien_config = get_Alien_config()

    # Load the offline document indexer for the app agent if available.
    if Alien_config.rag.offline_docs:
        console.print(
            f"📚 Loading offline help document indexer for {self._process_name}...",
            style="magenta",
        )
        self.build_offline_docs_retriever()

    # Load the online search indexer for the app agent if available.

    if Alien_config.rag.online_search and request:
        console.print("🔍 Creating a Bing search indexer...", style="magenta")
        self.build_online_search_retriever(
            request, Alien_config.rag.online_search_topk
        )

    # Load the experience indexer for the app agent if available.
    if Alien_config.rag.experience:
        console.print("📖 Creating an experience indexer...", style="magenta")
        experience_path = Alien_config.rag.experience_saved_path
        db_path = os.path.join(experience_path, "experience_db")
        self.build_experience_retriever(db_path)

    # Load the demonstration indexer for the app agent if available.
    if Alien_config.rag.demonstration:
        console.print("🎬 Creating an demonstration indexer...", style="magenta")
        demonstration_path = Alien_config.rag.demonstration_saved_path
        db_path = os.path.join(demonstration_path, "demonstration_db")
        self.build_human_demonstration_retriever(db_path)

    await self._load_mcp_context(context)
```

The `context_provision` method loads various knowledge retrievers based on the configuration settings in `config.yaml`:

- **Offline document retriever**: Loads indexed help documentation for the target application
- **Online search retriever**: Creates a Bing search indexer when a search request is provided
- **Experience retriever**: Loads the agent's historical successful experiences
- **Demonstration retriever**: Loads user-demonstrated action trajectories
- **MCP context**: Loads Model Context Protocol tool information for the current application

## Retriever API Reference

Alien employs the `Retriever` class located in `Alien/rag/retriever.py` to retrieve knowledge from various sources. For detailed API documentation, see:

:::rag.retriever.Retriever
