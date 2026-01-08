# DAG Visualization Test Suite

This directory contains a complete test suite for testing DAG visualization features.

## Directory Structure

```
tests/
├── run_dag_tests.py           # Main test runner
├── visualization/             # Visualization feature tests
│   ├── test_dag_simple.py     # Simple DAG test
│   ├── test_dag_mock.py       # Mock DAG visualization test
│   └── test_dag_demo.py       # Interactive DAG demo
└── integration/               # Integration tests
    └── test_e2e_galaxy.py     # End-to-end Galaxy framework test
```

## Test Description

### 1. Simple DAG Test (`test_dag_simple.py`)
- **Purpose**: Verify basic DAG visualization features
- **Features**: Minimal test to quickly verify core functionality
- **Runtime**: ~5 seconds

### 2. Mock DAG Visualization Test (`test_dag_mock.py`)
- **Purpose**: Test full DAG lifecycle using mock classes
- **Features**: Includes task creation, dependency addition, execution simulation
- **Runtime**: ~10 seconds

### 3. Interactive DAG Demo (`test_dag_demo.py`)
- **Purpose**: Showcase all visualization modes and features
- **Features**: Includes user interaction, demonstrating different visualization views
- **Runtime**: Variable (depends on user interaction)

### 4. End-to-end Galaxy Test (`test_e2e_galaxy.py`)
- **Purpose**: Complete system integration test
- **Features**: Tests real Galaxy framework workflow
- **Runtime**: ~15 seconds

## How to Run Tests

### Run All Tests
```bash
# In Alien root directory
python tests/run_dag_tests.py
```

### Run Single Test
```bash
# Simple Test
python tests/visualization/test_dag_simple.py

# Mock DAG Test
python tests/visualization/test_dag_mock.py

# Interactive Demo
python tests/visualization/test_dag_demo.py

# End-to-end Test
python tests/integration/test_e2e_galaxy.py
```

## Expected Output

All tests should display visualization output similar to the following:

### 1. Constellation Overview
```
─────── Task Constellation Overview ───────
╭────────── 📊 Constellation Info ───────────╮ ╭─ 📈 Statistics ─╮
│ ID: constellation_20250919_183339          │ │ Total Tasks: 5  │
│ Name: Sample DAG Demo                      │ │ Dependencies: 4 │
│ State: CREATED                             │ │ ✅ Completed: 0 │
╰────────────────────────────────────────────╯ ╰─────────────────╯
```

### 2. DAG Topology
```
📊 DAG Topology
🌌 Task Constellation
├── Layer 1
│   └── ⭕ task_1 (Initialize Project)
├── Layer 2
│   └── ⭕ task_2 (Load Data)
│       └── Dependencies: task_1
```

### 3. Task Details
```
📋 Task Details
╭──────────────┬───────────────┬──────────────┬──────────┬─────────────╮
│ ID           │ Name          │    Status    │ Priority │ Dependencies│
├──────────────┼───────────────┼──────────────┼──────────┼─────────────┤
│ task_1       │ Initialize    │  ⭕ pending  │    HIGH  │ none        │
╰──────────────┴───────────────┴──────────────┴──────────┴─────────────╯
```

## Troubleshooting

### Common Data
1. **Import Error**
   ```
   ❌ Import error: No module named 'ufo.galaxy.visualization.dag_visualizer'
   ```
   - Check if running from the correct directory
   - Ensure all dependencies are installed

2. **Visualizer Load Failure**
   ```
   ❌ Could not import DAGVisualizer: ...
   ```
   - Check if Rich library is installed: `pip install rich`
   - Verify DAGVisualizer class exists

## Test Requirements

### Environment Requirements
- Python 3.8+
- Rich library for console visualization
- All Alien framework dependencies

### System Requirements
- Console supporting Unicode characters
- Color output support (recommended)
