# API Reference

## Overview

This document provides comprehensive API documentation for the Orion Orchestrator system. The API is organized into three main components:

- **TaskOrionOrchestrator** - Main orchestration engine
- **OrionManager** - Device assignment and resource management  
- **OrionModificationSynchronizer** - Safe concurrent editing

## TaskOrionOrchestrator

The main orchestration engine that coordinates task execution across devices.

**Module**: `network.orion.orchestrator.orchestrator`

### Constructor

```python
TaskOrionOrchestrator(
    device_manager: Optional[OrionDeviceManager] = None,
    enable_logging: bool = True,
    event_bus = None
)
```

**Parameters**:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `device_manager` | `OrionDeviceManager` or `None` | Device manager for communication | `None` |
| `enable_logging` | `bool` | Enable logging output | `True` |
| `event_bus` | `EventBus` or `None` | Custom event bus instance | `None` (uses global) |

**Example**:
```python
from network.orion.orchestrator import TaskOrionOrchestrator
from network.client.device_manager import OrionDeviceManager

device_manager = OrionDeviceManager()
orchestrator = TaskOrionOrchestrator(
    device_manager=device_manager,
    enable_logging=True
)
```

### Core Methods

#### orchestrate_orion()

Main entry point for orchestrating a orion's execution.

```python
async def orchestrate_orion(
    self,
    orion: TaskOrion,
    device_assignments: Optional[Dict[str, str]] = None,
    assignment_strategy: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> Dict[str, Any]
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `orion` | `TaskOrion` | The orion to orchestrate | Yes |
| `device_assignments` | `Dict[str, str]` or `None` | Manual task→device mapping | No |
| `assignment_strategy` | `str` or `None` | Strategy: `"round_robin"`, `"capability_match"`, or `"load_balance"` | No |
| `metadata` | `Dict` or `None` | Additional orchestration metadata | No |

**Returns**: `Dict[str, Any]` with keys:
```python
{
    "results": {},  # Task results
    "status": "completed",  # Overall status
    "total_tasks": int,  # Number of tasks
    "statistics": {}  # Execution statistics
}
```

**Raises**:
- `ValueError`: Invalid DAG structure or device assignments
- `RuntimeError`: Orchestration execution error
- `asyncio.CancelledError`: Orchestration cancelled

**Example**:
```python
# With automatic assignment
results = await orchestrator.orchestrate_orion(
    orion=my_orion,
    assignment_strategy="capability_match"
)

# With manual assignments
device_assignments = {
    "task_1": "windows_main",
    "task_2": "android_device",
    "task_3": "windows_main"
}
results = await orchestrator.orchestrate_orion(
    orion=my_orion,
    device_assignments=device_assignments
)
```

#### execute_single_task()

Execute a single task independently (without orion context).

```python
async def execute_single_task(
    self,
    task: TaskStar,
    target_device_id: Optional[str] = None,
) -> Any
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `task` | `TaskStar` | Task to execute | Yes |
| `target_device_id` | `str` or `None` | Device for execution | No (auto-assigned if None) |

**Returns**: Task execution result content (extracts `result.result` from task execution)

**Raises**:
- `ValueError`: No available devices for task execution

**Example**:
```python
task = TaskStar(
    task_id="standalone_task",
    description="Collect system information"
)

result = await orchestrator.execute_single_task(
    task=task,
    target_device_id="windows_main"
)
```

#### get_orion_status()

Get detailed status of a orion during execution.

```python
async def get_orion_status(
    self, 
    orion: TaskOrion
) -> Dict[str, Any]
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `orion` | `TaskOrion` | Orion to query | Yes |

**Returns**: Status dictionary from OrionManager

**Note**: This method delegates to `OrionManager.get_orion_status()` using the orion's ID.

**Example**:
```python
status = await orchestrator.get_orion_status(orion)
if status:
    print(f"State: {status['state']}")
    print(f"Running: {len(status['running_tasks'])}")
```

#### get_available_devices()

Get list of available devices from device manager.

```python
async def get_available_devices(self) -> List[Dict[str, Any]]
```

**Returns**: List of device info dictionaries

**Example**:
```python
devices = await orchestrator.get_available_devices()
for device in devices:
    print(f"{device['device_id']}: {device['device_type']}")
```

### Configuration Methods

#### set_device_manager()

Set or update the device manager.

```python
def set_device_manager(
    self, 
    device_manager: OrionDeviceManager
) -> None
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `device_manager` | `OrionDeviceManager` | Device manager instance | Yes |

**Example**:
```python
new_device_manager = OrionDeviceManager()
orchestrator.set_device_manager(new_device_manager)
```

#### set_modification_synchronizer()

Attach a modification synchronizer for safe concurrent editing.

```python
def set_modification_synchronizer(
    self, 
    synchronizer: OrionModificationSynchronizer
) -> None
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `synchronizer` | `OrionModificationSynchronizer` | Synchronizer instance | Yes |

**Example**:
```python
from network.session.observers.orion_sync_observer import (
    OrionModificationSynchronizer
)

synchronizer = OrionModificationSynchronizer(orchestrator)
orchestrator.set_modification_synchronizer(synchronizer)
```

---

## OrionManager

Manages device assignments, resource allocation, and orion lifecycle.

**Module**: `network.orion.orchestrator.orion_manager`

### Constructor

```python
OrionManager(
    device_manager: Optional[OrionDeviceManager] = None,
    enable_logging: bool = True
)
```

**Parameters**:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `device_manager` | `OrionDeviceManager` or `None` | Device manager instance | `None` |
| `enable_logging` | `bool` | Enable logging | `True` |

### Device Assignment Methods

#### assign_devices_automatically()

Automatically assign devices to all tasks using a strategy.

```python
async def assign_devices_automatically(
    self,
    orion: TaskOrion,
    strategy: str = "round_robin",
    device_preferences: Optional[Dict[str, str]] = None,
) -> Dict[str, str]
```

**Parameters**:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `orion` | `TaskOrion` | Orion to assign | Required |
| `strategy` | `str` | Assignment strategy | `"round_robin"` |
| `device_preferences` | `Dict[str, str]` or `None` | Preferred task→device mappings | `None` |

**Strategies**:
- `"round_robin"`: Distribute tasks evenly
- `"capability_match"`: Match device types to task requirements
- `"load_balance"`: Minimize maximum device load

For more details on device assignment strategies, see [Orion Manager](orion_manager.md).

**Returns**: `Dict[str, str]` mapping task_id → device_id

**Raises**:
- `ValueError`: No available devices or invalid strategy

**Example**:
```python
assignments = await manager.assign_devices_automatically(
    orion,
    strategy="capability_match",
    device_preferences={"critical_task": "windows_main"}
)
```

#### reassign_task_device()

Reassign a single task to a different device.

```python
def reassign_task_device(
    self,
    orion: TaskOrion,
    task_id: str,
    new_device_id: str,
) -> bool
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `orion` | `TaskOrion` | Orion containing task | Yes |
| `task_id` | `str` | ID of task to reassign | Yes |
| `new_device_id` | `str` | New device ID | Yes |

**Returns**: `True` if successful, `False` if task not found

**Example**:
```python
success = manager.reassign_task_device(
    orion,
    task_id="task_5",
    new_device_id="android_backup"
)
```

#### clear_device_assignments()

Clear all device assignments from a orion.

```python
def clear_device_assignments(
    self, 
    orion: TaskOrion
) -> int
```

**Returns**: Number of assignments cleared

### Validation Methods

#### validate_orion_assignments()

Validate that all tasks have valid device assignments.

```python
def validate_orion_assignments(
    self, 
    orion: TaskOrion
) -> tuple[bool, List[str]]
```

**Returns**: `(is_valid, errors)` tuple

**Example**:
```python
is_valid, errors = manager.validate_orion_assignments(orion)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Lifecycle Methods

#### register_orion()

Register a orion for management tracking.

```python
def register_orion(
    self,
    orion: TaskOrion,
    metadata: Optional[Dict[str, Any]] = None,
) -> str
```

**Returns**: Orion ID

#### unregister_orion()

Unregister and clean up a orion.

```python
def unregister_orion(
    self, 
    orion_id: str
) -> bool
```

**Returns**: `True` if unregistered, `False` if not found

#### get_orion()

Get a managed orion by ID.

```python
def get_orion(
    self, 
    orion_id: str
) -> Optional[TaskOrion]
```

#### list_orions()

List all managed orions.

```python
def list_orions(self) -> List[Dict[str, Any]]
```

**Returns**: List of orion info dictionaries

### Status Methods

#### get_orion_status()

Get detailed status of a orion.

```python
async def get_orion_status(
    self, 
    orion_id: str
) -> Optional[Dict[str, Any]]
```

**Returns**: Status dictionary with keys:
```python
{
    "orion_id": str,
    "name": str,
    "state": str,
    "statistics": dict,
    "ready_tasks": List[str],
    "running_tasks": List[str],
    "completed_tasks": List[str],
    "failed_tasks": List[str],
    "metadata": dict
}
```

#### get_available_devices()

Get list of available devices.

```python
async def get_available_devices(self) -> List[Dict[str, Any]]
```

**Returns**: List of device info dictionaries:
```python
[
    {
        "device_id": str,
        "device_type": str,
        "capabilities": List[str],
        "status": str,
        "metadata": dict
    },
    ...
]
```

#### get_device_utilization()

Get device utilization statistics for a orion.

```python
def get_device_utilization(
    self, 
    orion: TaskOrion
) -> Dict[str, int]
```

**Returns**: `Dict[device_id, task_count]`

#### get_task_device_info()

Get device information for a specific task.

```python
def get_task_device_info(
    self,
    orion: TaskOrion,
    task_id: str
) -> Optional[Dict[str, Any]]
```

**Returns**: Device info dictionary or `None`

---

## OrionModificationSynchronizer

Synchronizes orion modifications with orchestrator execution to prevent race conditions.

**Module**: `network.session.observers.orion_sync_observer`

### Constructor

```python
OrionModificationSynchronizer(
    orchestrator: TaskOrionOrchestrator,
    logger: Optional[logging.Logger] = None
)
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `orchestrator` | `TaskOrionOrchestrator` | Orchestrator instance | Yes |
| `logger` | `logging.Logger` or `None` | Custom logger | No |

**Example**:
```python
synchronizer = OrionModificationSynchronizer(
    orchestrator=orchestrator,
    logger=logging.getLogger(__name__)
)
```

### Core Methods

#### on_event()

Handle orchestration events (implements `IEventObserver`).

```python
async def on_event(self, event: Event) -> None
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `event` | `Event` | Event to process | Yes |

**Events handled**:
- `TASK_COMPLETED`: Register pending modification
- `TASK_FAILED`: Register pending modification
- `ORION_MODIFIED`: Complete pending modifications

#### wait_for_pending_modifications()

Wait for all pending modifications to complete.

```python
async def wait_for_pending_modifications(
    self, 
    timeout: Optional[float] = None
) -> bool
```

**Parameters**:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `timeout` | `float` or `None` | Timeout in seconds | `None` (uses default: 600s) |

**Returns**: `True` if all completed, `False` if timeout

**Example**:
```python
# In orchestration loop
completed = await synchronizer.wait_for_pending_modifications(timeout=300.0)
if not completed:
    logger.warning("Modifications timed out")
```

#### merge_and_sync_orion_states()

Merge agent's structural changes with orchestrator's execution state.

```python
def merge_and_sync_orion_states(
    self,
    orchestrator_orion: TaskOrion,
) -> TaskOrion
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `orchestrator_orion` | `TaskOrion` | Orchestrator's orion | Yes |

**Returns**: Merged orion with consistent state

**Example**:
```python
merged = synchronizer.merge_and_sync_orion_states(
    orchestrator_orion=current_orion
)
```

### Configuration Methods

#### set_modification_timeout()

Set the timeout for modifications.

```python
def set_modification_timeout(self, timeout: float) -> None
```

**Parameters**:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `timeout` | `float` | Timeout in seconds (must be > 0) | Yes |

**Raises**: `ValueError` if timeout ≤ 0

**Example**:
```python
# Increase timeout for slow LLM responses
synchronizer.set_modification_timeout(1800.0)  # 30 minutes
```

### Query Methods

#### has_pending_modifications()

Check if any modifications are pending.

```python
def has_pending_modifications(self) -> bool
```

**Returns**: `True` if modifications pending

#### get_pending_count()

Get number of pending modifications.

```python
def get_pending_count(self) -> int
```

#### get_pending_task_ids()

Get list of task IDs with pending modifications.

```python
def get_pending_task_ids(self) -> list
```

#### get_current_orion()

Get the orion currently being modified.

```python
def get_current_orion(self) -> Optional[TaskOrion]
```

#### get_statistics()

Get synchronization statistics.

```python
def get_statistics(self) -> Dict[str, int]
```

**Returns**:
```python
{
    "total_modifications": int,
    "completed_modifications": int,
    "timeout_modifications": int
}
```

### Utility Methods

#### clear_pending_modifications()

⚠️ **Emergency use only**: Forcefully clear all pending modifications.

```python
def clear_pending_modifications(self) -> None
```

---

## Common Usage Patterns

### Basic Orchestration

```python
from network.orion.orchestrator import TaskOrionOrchestrator
from network.client.device_manager import OrionDeviceManager

# Setup
device_manager = OrionDeviceManager()
orchestrator = TaskOrionOrchestrator(device_manager)

# Create orion
orion = TaskOrion(name="MyWorkflow")
# ... add tasks and dependencies ...

# Orchestrate
results = await orchestrator.orchestrate_orion(
    orion,
    assignment_strategy="round_robin"
)

print(f"Status: {results['status']}")
print(f"Total tasks: {results['total_tasks']}")
```

### With Synchronization

```python
from network.session.observers.orion_sync_observer import (
    OrionModificationSynchronizer
)
from network.core.events import get_event_bus

# Setup orchestrator
orchestrator = TaskOrionOrchestrator(device_manager)

# Attach synchronizer
synchronizer = OrionModificationSynchronizer(orchestrator)
orchestrator.set_modification_synchronizer(synchronizer)

# Subscribe to events
event_bus = get_event_bus()
event_bus.subscribe(synchronizer)

# Orchestrate with automatic synchronization
results = await orchestrator.orchestrate_orion(orion)
```

For details on the synchronization protocol, see [Safe Assignment Locking](safe_assignment_locking.md).

### Custom Event Handling

```python
from network.core.events import IEventObserver, Event, EventType

class ProgressTracker(IEventObserver):
    async def on_event(self, event: Event):
        if event.event_type == EventType.TASK_COMPLETED:
            print(f"✓ {event.task_id} completed")
        elif event.event_type == EventType.TASK_FAILED:
            print(f"✗ {event.task_id} failed")

# Subscribe
tracker = ProgressTracker()
event_bus.subscribe(tracker, {
    EventType.TASK_COMPLETED,
    EventType.TASK_FAILED
})

# Orchestrate with tracking
results = await orchestrator.orchestrate_orion(orion)
```

For more details on event handling, see [Event-Driven Coordination](event_driven_coordination.md).

### Manual Device Assignment

```python
# Method 1: Pre-assign in tasks
for task in orion.get_all_tasks():
    if "windows" in task.description.lower():
        task.target_device_id = "windows_main"
    elif "android" in task.description.lower():
        task.target_device_id = "android_device"

# Method 2: Manual assignment dict
device_assignments = {
    task.task_id: determine_device(task)
    for task in orion.get_all_tasks()
}

results = await orchestrator.orchestrate_orion(
    orion,
    device_assignments=device_assignments
)
```

## Type Definitions

### TaskOrion

See [TaskOrion documentation](../orion/task_orion.md)

### TaskStar

See [TaskStar documentation](../orion/task_star.md)

### Event Types

```python
from network.core.events import EventType

EventType.TASK_STARTED          # Task execution begins
EventType.TASK_COMPLETED        # Task completes successfully
EventType.TASK_FAILED           # Task fails
EventType.ORION_STARTED # Orchestration begins
EventType.ORION_COMPLETED  # All tasks finished
EventType.ORION_FAILED     # Orchestration failed
EventType.ORION_MODIFIED   # DAG structure updated
```

## Error Handling

### Common Exceptions

| Exception | Cause | Handling |
|-----------|-------|----------|
| `ValueError` | Invalid DAG, missing assignments | Validate before orchestration |
| `RuntimeError` | Execution error | Check device connectivity |
| `asyncio.TimeoutError` | Task timeout | Increase task timeout |
| `asyncio.CancelledError` | Orchestration cancelled | Cleanup resources |

### Example Error Handling

```python
try:
    results = await orchestrator.orchestrate_orion(
        orion,
        assignment_strategy="capability_match"
    )
except ValueError as e:
    logger.error(f"Invalid orion: {e}")
    # Fix validation errors
except RuntimeError as e:
    logger.error(f"Execution failed: {e}")
    # Retry or alert
except asyncio.CancelledError:
    logger.warning("Orchestration cancelled")
    # Cleanup
finally:
    # Always cleanup
    await device_manager.disconnect_all()
```

## Related Documentation

- **[Overview](overview.md)** - System architecture and design
- **[Event-Driven Coordination](event_driven_coordination.md)** - Event system details
- **[Asynchronous Scheduling](asynchronous_scheduling.md)** - Execution model
- **[Safe Assignment Locking](safe_assignment_locking.md)** - Synchronization protocol
- **[Consistency Guarantees](consistency_guarantees.md)** - Invariants and validation
- **[Batched Editing](batched_editing.md)** - Efficiency optimizations
- **[Orion Manager](orion_manager.md)** - Resource management

---

## Getting Help

Check the examples directory for complete code samples or see [GitHub issues](https://github.com/DEVELOPER-DEEVEN/alien-project/issues) for known problems.
