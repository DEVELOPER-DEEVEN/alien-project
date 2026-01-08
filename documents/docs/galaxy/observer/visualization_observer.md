# DAG Visualization Observer

The **DAGVisualizationObserver** provides real-time visual feedback during network execution. It displays DAG topology, task progress, and network modifications using rich terminal graphics.

**Location:** `cluster/session/observers/dag_visualization_observer.py`

## Purpose

The Visualization Observer enables developers and users to:

- **See DAG Structure** — View network topology and task dependencies
- **Monitor Progress** — Track task execution in real-time
- **Observe Modifications** — Visualize how the network changes
- **Debug Issues** — Identify bottlenecks and failed tasks visually

## Architecture

The observer uses a **delegation pattern** with specialized handlers:

```mermaid
graph TB
    subgraph "Main Observer"
        DVO[DAGVisualizationObserver]
        CE[network Events]
        TE[Task Events]
    end
    
    subgraph "Specialized Handlers"
        CVH[networkVisualizationHandler]
        TVH[TaskVisualizationHandler]
    end
    
    subgraph "Display Components"
        CD[networkDisplay]
        TD[TaskDisplay]
        DV[DAGVisualizer]
    end
    
    DVO --> CE
    DVO --> TE
    CE --> CVH
    TE --> TVH
    
    CVH --> CD
    CVH --> DV
    TVH --> TD
    TVH --> DV
    
    style DVO fill:#66bb6a,stroke:#333,stroke-width:3px
    style CVH fill:#ffa726,stroke:#333,stroke-width:2px
    style TVH fill:#ffa726,stroke:#333,stroke-width:2px
```

**Component Responsibilities:**

| Component | Role | Handled Events |
|-----------|------|----------------|
| **DAGVisualizationObserver** | Main coordinator, routes events | All network and task events |
| **networkVisualizationHandler** | Handles network-level displays | network_STARTED, COMPLETED, MODIFIED |
| **TaskVisualizationHandler** | Handles task-level displays | TASK_STARTED, COMPLETED, FAILED |
| **DAGVisualizer** | Renders complex DAG visualizations | Used by handlers for topology |
| **networkDisplay** | Renders network information | Used by handler for network events |
| **TaskDisplay** | Renders task information | Used by handler for task events |

## Implementation

### Initialization

```python
from cluster.session.observers import DAGVisualizationObserver
from rich.console import Console

# Create visualization observer
viz_observer = DAGVisualizationObserver(
    enable_visualization=True,
    console=Console()  # Optional: provide custom console
)

# Subscribe to event bus
from cluster.core.events import get_event_bus
event_bus = get_event_bus()
event_bus.subscribe(viz_observer)
```

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_visualization` | `bool` | `True` | Whether to enable visualization |
| `console` | `rich.Console` | `None` | Optional rich console for output |

### Disabling Visualization

Visualization can be toggled at runtime:

```python
# Disable visualization temporarily
viz_observer.set_visualization_enabled(False)

# Re-enable
viz_observer.set_visualization_enabled(True)
```

## Visualization Types

The observer produces several types of visualizations:

### 1. network Started

Displays when a network begins execution:

```
╭──────────────────────────────────────────────────────────────╮
│ 🌟 network Started: email_batch_network          │
├──────────────────────────────────────────────────────────────┤
│ ID: const_abc123                                             │
│ Total Tasks: 8                                               │
│ Status: ACTIVE                                               │
│ Parallel Capacity: 3                                         │
╰──────────────────────────────────────────────────────────────╯
```

Followed by DAG topology:

```mermaid
graph TD
    fetch_emails[Fetch Emails]
    parse_1[Parse Email 1]
    parse_2[Parse Email 2]
    parse_3[Parse Email 3]
    reply_1[Reply Email 1]
    reply_2[Reply Email 2]
    reply_3[Reply Email 3]
    summarize[Summarize Results]
    
    fetch_emails --> parse_1
    fetch_emails --> parse_2
    fetch_emails --> parse_3
    parse_1 --> reply_1
    parse_2 --> reply_2
    parse_3 --> reply_3
    reply_1 --> summarize
    reply_2 --> summarize
    reply_3 --> summarize
```

### 2. Task Progress

Displays task execution events:

**Task Started:**
```
▶ Task Started: parse_email_1
  └─ Type: parse_email
  └─ Device: windows_pc_001
  └─ Priority: MEDIUM
```

**Task Completed:**
```
✅ Task Completed: parse_email_1
   Duration: 2.3s
   Result: Parsed 1 email with 2 attachments
   Newly Ready: [reply_email_1]
```

**Task Failed:**
```
❌ Task Failed: parse_email_2
   Duration: 1.8s
   Error: NetworkTimeout: Failed to connect to email server
   Retry: 1/3
   Newly Ready: []
```

### 3. network Modified

Shows structural changes to the network:

```
🔄 network Modified: email_batch_network
   Modification Type: add_tasks
   On Task: parse_email_1
   
   Changes:
   ├─ Tasks Added: 2
   │  └─ extract_attachment_1
   │  └─ extract_attachment_2
   ├─ Dependencies Added: 2
   │  └─ parse_email_1 → extract_attachment_1
   │  └─ parse_email_1 → extract_attachment_2
   └─ Tasks Modified: 1
      └─ reply_email_1 (dependencies updated)
```

Followed by updated DAG topology showing new tasks.

### 4. Execution Flow

Shows current execution state (for smaller networks):

```
Execution Flow:
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃ Task ID         ┃ Status    ┃ Device  ┃ Duration ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ fetch_emails    │ COMPLETED │ win_001 │ 1.2s     │
│ parse_email_1   │ RUNNING   │ win_001 │ 0.8s...  │
│ parse_email_2   │ RUNNING   │ mac_002 │ 0.5s...  │
│ parse_email_3   │ PENDING   │ -       │ -        │
│ reply_email_1   │ PENDING   │ -       │ -        │
└─────────────────┴───────────┴─────────┴──────────┘
```

## Event Handling Flow

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant EB as EventBus
    participant DVO as DAGVisualizationObserver
    participant CVH as networkHandler
    participant TVH as TaskHandler
    participant D as Display Components
    
    O->>EB: network_STARTED
    EB->>DVO: on_event(event)
    DVO->>CVH: handle_network_event()
    CVH->>D: Display network start
    CVH->>D: Display DAG topology
    
    O->>EB: TASK_STARTED
    EB->>DVO: on_event(event)
    DVO->>TVH: handle_task_event()
    TVH->>D: Display task start
    
    O->>EB: TASK_COMPLETED
    EB->>DVO: on_event(event)
    DVO->>TVH: handle_task_event()
    TVH->>D: Display task completion
    TVH->>D: Display execution flow
    
    Note over O: Agent modifies network
    
    O->>EB: network_MODIFIED
    EB->>DVO: on_event(event)
    DVO->>CVH: handle_network_event()
    CVH->>D: Display modifications
    CVH->>D: Display updated topology
```

## API Reference

### Main Observer Methods

#### Constructor

```python
def __init__(
    self, 
    enable_visualization: bool = True, 
    console=None
)
```

**Parameters:**

- `enable_visualization` — Enable/disable visualization output
- `console` — Optional `rich.Console` for output control

#### set_visualization_enabled()

Toggle visualization at runtime:

```python
def set_visualization_enabled(self, enabled: bool) -> None
```

**Example:**

```python
# Disable during bulk operations
viz_observer.set_visualization_enabled(False)
await orchestrator.execute_network(network)

# Re-enable for interactive use
viz_observer.set_visualization_enabled(True)
```

### network Management

#### register_network()

Manually register a network for visualization:

```python
def register_network(
    self,
    network_id: str, 
    network: Tasknetwork
) -> None
```

**Use Case:** Pre-register networks before execution starts.

#### get_network()

Retrieve stored network reference:

```python
def get_network(self, network_id: str) -> Optional[Tasknetwork]
```

#### clear_networks()

Clear all stored network references:

```python
def clear_networks(self) -> None
```

## Customization

### Custom Console

Provide custom Rich console for output control:

```python
from rich.console import Console

# Console with custom width and theme
custom_console = Console(
    width=120,
    theme=my_custom_theme,
    record=True  # Enable recording for export
)

viz_observer = DAGVisualizationObserver(
    enable_visualization=True,
    console=custom_console
)
```

### Selective Visualization

Visualize only specific event types:

```python
from cluster.core.events import EventType

# Subscribe to specific events only
event_bus.subscribe(viz_observer, {
    EventType.network_STARTED,
    EventType.network_MODIFIED,
    EventType.TASK_FAILED  # Only show failures
})
```

## Usage Examples

### Example 1: Basic Visualization

```python
from cluster.session.observers import DAGVisualizationObserver
from cluster.core.events import get_event_bus

async def visualize_execution():
    """Execute network with visualization."""
    
    # Create and subscribe visualization observer
    viz_observer = DAGVisualizationObserver(enable_visualization=True)
    event_bus = get_event_bus()
    event_bus.subscribe(viz_observer)
    
    # Execute network (visualization happens automatically)
    await orchestrator.execute_network(network)
    
    # Clean up
    event_bus.unsubscribe(viz_observer)
```

### Example 2: Conditional Visualization

```python
async def execute_with_conditional_viz(network, verbose: bool = False):
    """Execute with visualization only if verbose mode enabled."""
    
    viz_observer = DAGVisualizationObserver(enable_visualization=verbose)
    event_bus = get_event_bus()
    
    if verbose:
        event_bus.subscribe(viz_observer)
    
    try:
        await orchestrator.execute_network(network)
    finally:
        if verbose:
            event_bus.unsubscribe(viz_observer)
```

### Example 3: Export Visualization

```python
from rich.console import Console

async def execute_and_export_visualization():
    """Execute network and export visualization to HTML."""
    
    # Create console with recording enabled
    console = Console(record=True, width=120)
    viz_observer = DAGVisualizationObserver(
        enable_visualization=True,
        console=console
    )
    
    event_bus = get_event_bus()
    event_bus.subscribe(viz_observer)
    
    try:
        await orchestrator.execute_network(network)
    finally:
        event_bus.unsubscribe(viz_observer)
    
    # Export recorded output to HTML
    console.save_html("execution_visualization.html")
    print("Visualization saved to execution_visualization.html")
```

### Example 4: Multiple networks

```python
async def visualize_multiple_networks():
    """Visualize multiple network executions."""
    
    viz_observer = DAGVisualizationObserver(enable_visualization=True)
    event_bus = get_event_bus()
    event_bus.subscribe(viz_observer)
    
    try:
        for network in networks:
            print(f"\n{'='*60}")
            print(f"Executing: {network.name}")
            print(f"{'='*60}\n")
            
            await orchestrator.execute_network(network)
            
            # Clear network references between executions
            viz_observer.clear_networks()
    finally:
        event_bus.unsubscribe(viz_observer)
```

## Performance Considerations

### Visualization Overhead

Visualization adds minimal overhead:

- **Small DAGs** (< 10 tasks): Negligible impact
- **Medium DAGs** (10-50 tasks): < 1% overhead
- **Large DAGs** (> 50 tasks): Topology rendering may be slow

### Optimization Strategies

```python
# Strategy 1: Disable for large networks
if network.task_count > 50:
    viz_observer.set_visualization_enabled(False)

# Strategy 2: Subscribe to fewer events
event_bus.subscribe(viz_observer, {
    EventType.network_STARTED,
    EventType.network_COMPLETED,
    EventType.TASK_FAILED  # Only show problems
})

# Strategy 3: Conditional topology display
# (Handler automatically skips topology for networks > 10 tasks)
```

## Best Practices

### 1. Enable for Interactive Sessions

```python
# ✅ Good: Interactive development/debugging
if __name__ == "__main__":
    viz_observer = DAGVisualizationObserver(enable_visualization=True)
    # ...

# ✅ Good: Batch processing
if running_in_batch_mode:
    viz_observer = DAGVisualizationObserver(enable_visualization=False)
```

### 2. Clean Up network References

```python
# After processing many networks
for network in network_list:
    await orchestrator.execute_network(network)
    viz_observer.clear_networks()  # Free memory
```

### 3. Export for Documentation

```python
# Record visualization for documentation/reports
console = Console(record=True)
viz_observer = DAGVisualizationObserver(console=console)

# ... execute network ...

# Export
console.save_html("docs/execution_example.html")
console.save_text("logs/execution.txt")
```

## Related Documentation

- **[Observer System Overview](overview.md)** — Architecture and design
- **[Progress Observer](progress_observer.md)** — Task completion tracking

## Summary

The DAG Visualization Observer:

- **Displays** network structure and execution progress
- **Delegates** to specialized handlers for clean separation
- **Uses** Rich terminal graphics for beautiful output
- **Supports** conditional enabling/disabling
- **Exports** visualization for documentation

This observer is essential for understanding and debugging network execution, providing intuitive visual feedback for complex DAG workflows.
