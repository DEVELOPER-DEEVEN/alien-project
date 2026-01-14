#!/usr/bin/env python3
"""
End-to-End TaskOrion Demo

This comprehensive demo tests the entire pipeline from LLM DAG string input
to task execution and DAG updates using the alien.network framework.

Test Coverage:
- Various DAG structures (linear, parallel, diamond, complex branching)
- LLM parsing and orion creation
- Device assignment and task execution
- DAG updates and modifications
- Error handling and recovery
- Performance and statistics tracking
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import Network orion components
from network.orion import (
    TaskOrionOrchestrator,
    TaskOrion,
    TaskStar,
    TaskStarLine,
    LLMParser,
    TaskStatus,
    DependencyType,
    OrionState,
    DeviceType,
    TaskPriority,
    create_and_orchestrate_from_llm,
    create_simple_orion,
)

# Import Network client components directly
from network.client.orion_client import OrionClient
from network.client.config_loader import OrionConfig, DeviceConfig

# Import Network session and agent components
from network.session import NetworkSession
from network.agents import NetworkWeaverAgent
from network.agents.network_agent import MockNetworkWeaverAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockDeviceManager:
    """Mock device manager to match OrionDeviceManager interface."""

    def __init__(self, connected_devices: Dict[str, Any]):
        self.connected_devices = connected_devices
        self.device_registry = MockDeviceRegistry(connected_devices)

    def get_connected_devices(self) -> List[str]:
        """Get list of connected device IDs."""
        return [
            device_id
            for device_id, info in self.connected_devices.items()
            if info["status"] == "connected"
        ]

    async def assign_task_to_device(
        self,
        task_id: str,
        device_id: str,
        target_client_id: Optional[str] = None,
        task_description: str = "",
        task_data: Dict[str, Any] = None,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """Mock task assignment that simulates device execution."""
        if device_id not in self.connected_devices:
            raise ValueError(f"Device {device_id} not found")

        # Simulate task execution
        device_info = self.connected_devices[device_id]
        return {
            "result": f"Mock result from {device_id}",
            "device_id": device_id,
            "task_id": task_id,
            "status": "completed",
            "device_type": device_info.get("device_type", "unknown"),
            "execution_time": 0.5,
        }


class MockDeviceRegistry:
    """Mock device registry."""

    def __init__(self, connected_devices: Dict[str, Any]):
        self.connected_devices = connected_devices

    def get_device_info(self, device_id: str):
        """Get device info for a device."""
        if device_id in self.connected_devices:
            device_data = self.connected_devices[device_id]
            return type(
                "AgentProfile",
                (),
                {
                    "device_type": device_data.get("device_type", "unknown"),
                    "capabilities": device_data.get("capabilities", []),
                    "metadata": device_data.get("metadata", {}),
                },
            )()
        return None


class MockNetworkOrionClient:
    """
    Enhanced Mock client that simulates OrionClient interface
    with realistic multi-device scenarios.
    """

    def __init__(self):
        self.connected_devices = {
            "web_device_01": {
                "device_type": "web",
                "capabilities": [
                    "web_search",
                    "web_navigation",
                    "data_extraction",
                    "screenshot",
                ],
                "status": "connected",
                "metadata": {
                    "browser": "chrome",
                    "version": "1.0",
                    "location": "cloud",
                },
                "load": 0.2,
                "performance_score": 0.9,
            },
            "office_device_01": {
                "device_type": "office",
                "capabilities": [
                    "word_processing",
                    "excel_operations",
                    "ppt_creation",
                    "pdf_generation",
                ],
                "status": "connected",
                "metadata": {
                    "office_version": "365",
                    "version": "1.0",
                    "location": "local",
                },
                "load": 0.1,
                "performance_score": 0.95,
            },
            "mobile_device_01": {
                "device_type": "mobile",
                "capabilities": ["app_automation", "messaging", "camera", "contacts"],
                "status": "connected",
                "metadata": {
                    "platform": "android",
                    "version": "1.0",
                    "location": "cloud",
                },
                "load": 0.3,
                "performance_score": 0.85,
            },
            "desktop_device_01": {
                "device_type": "desktop",
                "capabilities": [
                    "file_operations",
                    "system_admin",
                    "development",
                    "automation",
                ],
                "status": "connected",
                "metadata": {"os": "windows", "version": "1.0", "location": "local"},
                "load": 0.4,
                "performance_score": 0.88,
            },
            "cloud_service_01": {
                "device_type": "cloud",
                "capabilities": [
                    "data_processing",
                    "ml_inference",
                    "api_calls",
                    "storage",
                ],
                "status": "connected",
                "metadata": {
                    "provider": "azure",
                    "version": "1.0",
                    "location": "cloud",
                },
                "load": 0.15,
                "performance_score": 0.92,
            },
        }
        self.task_execution_log = []

        # Add mock device manager to match the OrionClient interface
        self.device_manager = MockDeviceManager(self.connected_devices)

    def get_connected_devices(self) -> List[str]:
        """Get list of connected device IDs."""
        return [
            device_id
            for device_id, info in self.connected_devices.items()
            if info["status"] == "connected"
        ]

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status information."""
        return self.connected_devices.get(device_id, {})

    async def execute_task(
        self,
        request: str,
        device_id: str,
        task_name: str = None,
        metadata: Dict[str, Any] = None,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """
        Execute task on device with realistic simulation.
        """
        start_time = time.time()
        device_info = self.connected_devices.get(device_id, {})

        # Simulate execution time based on task complexity and device performance
        base_time = 0.5
        performance_factor = device_info.get("performance_score", 0.8)
        load_factor = 1 + device_info.get("load", 0.5)

        execution_time = base_time * load_factor / performance_factor

        # Add some randomness to simulate real-world variance
        import random

        execution_time *= 0.8 + 0.4 * random.random()

        await asyncio.sleep(execution_time)

        # Simulate occasional failures (5% chance)
        if random.random() < 0.05:
            raise Exception(f"Simulated device failure on {device_id}")

        result = {
            "task_id": task_name or "unnamed_task",
            "device_id": device_id,
            "status": "completed",
            "result": {
                "message": f"Successfully executed '{request}' on {device_id}",
                "execution_details": {
                    "device_type": device_info.get("device_type", "unknown"),
                    "capabilities_used": device_info.get("capabilities", [])[
                        :2
                    ],  # Simulate used capabilities
                    "performance_metrics": {
                        "execution_time": execution_time,
                        "device_load_before": device_info.get("load", 0),
                        "device_load_after": min(1.0, device_info.get("load", 0) + 0.1),
                    },
                },
            },
            "metadata": metadata or {},
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
        }

        # Log execution
        self.task_execution_log.append(
            {
                "task_name": task_name,
                "device_id": device_id,
                "request": request,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Update device load
        if device_id in self.connected_devices:
            current_load = self.connected_devices[device_id].get("load", 0)
            self.connected_devices[device_id]["load"] = min(1.0, current_load + 0.05)

        return result


class E2EOrionTester:
    """
    Comprehensive end-to-end tester for TaskOrion system.
    """

    def __init__(self):
        self.mock_client = MockNetworkOrionClient()
        self.orchestrator = TaskOrionOrchestrator(
            device_manager=self.mock_client.device_manager, enable_logging=True
        )
        self.test_results = {}
        self.performance_metrics = {}

    def create_mock_llm_responses(self) -> Dict[str, str]:
        """
        Create various mock LLM responses for different DAG structures.
        """
        return {
            "linear_workflow": """
            Tasks:
            1. init_project: Initialize new research project
            2. gather_requirements: Gather project requirements from stakeholders  
            3. create_timeline: Create project timeline and milestones
            4. assign_resources: Assign team members and resources
            5. finalize_plan: Review and finalize project plan
            
            Dependencies:
            - init_project must complete before gather_requirements
            - gather_requirements must complete before create_timeline
            - create_timeline must complete before assign_resources
            - assign_resources must complete before finalize_plan
            """,
            "parallel_workflow": """
            Tasks:
            1. data_collection: Collect market research data
            2. web_scraping: Scrape competitor websites
            3. survey_analysis: Analyze customer survey results
            4. social_listening: Monitor social media mentions
            5. report_synthesis: Synthesize all findings into report
            
            Dependencies:
            - data_collection, web_scraping, survey_analysis, social_listening can run in parallel
            - report_synthesis requires completion of all parallel tasks
            """,
            "diamond_workflow": """
            Tasks:
            1. start_analysis: Begin data analysis workflow
            2. clean_data: Clean and preprocess raw data
            3. feature_engineering: Create new features from data
            4. model_training: Train machine learning model
            5. model_validation: Validate model performance
            6. generate_report: Generate final analysis report
            
            Dependencies:
            - start_analysis triggers both clean_data and feature_engineering
            - model_training requires both clean_data and feature_engineering
            - model_validation requires model_training
            - generate_report requires both model_training and model_validation
            """,
            "complex_branching": """
            Tasks:
            1. project_kickoff: Initialize complex project
            2. research_phase: Conduct initial research
            3. design_architecture: Design system architecture
            4. develop_frontend: Develop user interface
            5. develop_backend: Develop server logic
            6. setup_database: Configure database systems
            7. integration_testing: Test system integration
            8. performance_testing: Test system performance
            9. security_audit: Conduct security review
            10. deployment_prep: Prepare for deployment
            11. production_deploy: Deploy to production
            
            Dependencies:
            - project_kickoff starts research_phase
            - research_phase enables design_architecture
            - design_architecture enables develop_frontend, develop_backend, setup_database in parallel
            - integration_testing requires develop_frontend and develop_backend
            - performance_testing requires integration_testing and setup_database
            - security_audit requires develop_backend and setup_database
            - deployment_prep requires performance_testing and security_audit
            - production_deploy requires deployment_prep
            """,
            "conditional_workflow": """
            Tasks:
            1. evaluate_proposal: Review business proposal
            2. budget_analysis: Analyze budget requirements
            3. risk_assessment: Assess project risks
            4. stakeholder_approval: Get stakeholder sign-off
            5. project_execution: Execute approved project
            6. alternative_plan: Create alternative approach
            7. final_decision: Make final go/no-go decision
            
            Dependencies:
            - evaluate_proposal enables budget_analysis and risk_assessment in parallel
            - stakeholder_approval requires budget_analysis (if budget approved)
            - project_execution requires stakeholder_approval (if approved)
            - alternative_plan triggers if risk_assessment identifies high risk
            - final_decision requires either project_execution or alternative_plan
            """,
        }

    async def test_dag_structure(
        self, dag_name: str, llm_response: str
    ) -> Dict[str, Any]:
        """
        Test a specific DAG structure.
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing DAG Structure: {dag_name.upper()}")
        logger.info(f"{'='*60}")

        start_time = time.time()

        try:
            # Step 1: Parse LLM response to create orion
            logger.info("📝 Step 1: Parsing LLM response...")
            orion = await self.orchestrator.create_orion_from_llm(
                llm_response, f"{dag_name}_orion"
            )

            logger.info(
                f"✅ Created orion: {orion.task_count} tasks, {orion.dependency_count} dependencies"
            )

            # Step 2: Validate DAG structure
            logger.info("🔍 Step 2: Validating DAG structure...")
            is_valid, errors = orion.validate_dag()
            if not is_valid:
                logger.error(f"❌ DAG validation failed: {errors}")
                return {
                    "status": "failed",
                    "error": "DAG validation failed",
                    "errors": errors,
                }

            logger.info("✅ DAG structure is valid")

            # Step 3: Display orion structure
            logger.info("📊 Step 3: Analyzing orion structure...")
            self._display_orion_info(orion)

            # Step 4: Assign devices automatically
            logger.info("🎯 Step 4: Assigning devices to tasks...")
            await self.orchestrator.assign_devices_automatically(orion)

            # Display device assignments
            logger.info("Device assignments:")
            for task in orion.tasks.values():
                logger.info(
                    f"   - {task.task_id}: {task.description[:50]}... → {task.target_device_id}"
                )

            # Step 5: Execute orion
            logger.info("🚀 Step 5: Executing orion...")

            progress_log = []

            def progress_callback(task_id: str, status: TaskStatus, result: Any):
                progress_log.append(
                    {
                        "task_id": task_id,
                        "status": status.value,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                logger.info(f"📈 Progress: {task_id} → {status.value}")

            execution_result = await self.orchestrator.orchestrate_orion(
                orion, progress_callback=progress_callback
            )

            # Step 6: Analyze results
            logger.info("📊 Step 6: Analyzing execution results...")
            end_time = time.time()
            total_time = end_time - start_time

            # Get final orion status
            final_status = await self.orchestrator.get_orion_status(
                orion
            )

            test_result = {
                "dag_name": dag_name,
                "status": execution_result.get("status", "unknown"),
                "total_execution_time": total_time,
                "orion_stats": final_status["statistics"],
                "executor_stats": final_status["executor_stats"],
                "progress_log": progress_log,
                "task_results": {},
                "device_utilization": self._analyze_device_utilization(),
                "dag_characteristics": self._analyze_dag_characteristics(orion),
            }

            # Collect individual task results
            for task in orion.tasks.values():
                test_result["task_results"][task.task_id] = {
                    "status": task.status.value,
                    "execution_time": getattr(task, "execution_duration", 0),
                    "device_assigned": task.target_device_id,
                    "result": task.result,
                }

            logger.info(f"✅ Test completed successfully in {total_time:.2f}s")
            logger.info(f"   - Final status: {execution_result.get('status')}")
            logger.info(f"   - Tasks completed: {len(final_status['completed_tasks'])}")
            logger.info(f"   - Tasks failed: {len(final_status['failed_tasks'])}")

            return test_result

        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}")
            logger.error(traceback.format_exc())

            return {
                "dag_name": dag_name,
                "status": "failed",
                "error": str(e),
                "total_execution_time": time.time() - start_time,
                "traceback": traceback.format_exc(),
            }

    def _display_orion_info(self, orion: TaskOrion):
        """Display detailed orion information."""
        logger.info(f"Orion: {orion.name}")
        logger.info(f"  - ID: {orion.orion_id}")
        logger.info(f"  - State: {orion.state.value}")
        logger.info(f"  - Tasks: {orion.task_count}")
        logger.info(f"  - Dependencies: {orion.dependency_count}")

        # Show task breakdown by device type
        device_types = {}
        for task in orion.tasks.values():
            device_type = task.device_type.value if task.device_type else "unassigned"
            device_types[device_type] = device_types.get(device_type, 0) + 1

        logger.info(f"  - Device type distribution: {device_types}")

        # Show dependency types
        dep_types = {}
        for dep in orion.dependencies.values():
            dep_type = dep.dependency_type.value
            dep_types[dep_type] = dep_types.get(dep_type, 0) + 1

        logger.info(f"  - Dependency type distribution: {dep_types}")

        # Show topological order
        try:
            topo_order = orion.get_topological_order()
            logger.info(
                f"  - Execution order: {' → '.join(topo_order[:5])}{'...' if len(topo_order) > 5 else ''}"
            )
        except Exception as e:
            logger.warning(f"  - Could not determine execution order: {e}")

    def _analyze_device_utilization(self) -> Dict[str, Any]:
        """Analyze device utilization during test execution."""
        utilization = {}

        for device_id, device_info in self.mock_client.connected_devices.items():
            # Count tasks executed on this device
            tasks_executed = len(
                [
                    log
                    for log in self.mock_client.task_execution_log
                    if log["device_id"] == device_id
                ]
            )

            total_execution_time = sum(
                [
                    log["execution_time"]
                    for log in self.mock_client.task_execution_log
                    if log["device_id"] == device_id
                ]
            )

            utilization[device_id] = {
                "device_type": device_info.get("device_type"),
                "tasks_executed": tasks_executed,
                "total_execution_time": total_execution_time,
                "final_load": device_info.get("load", 0),
                "performance_score": device_info.get("performance_score", 0),
                "capabilities": device_info.get("capabilities", []),
            }

        return utilization

    def _analyze_dag_characteristics(
        self, orion: TaskOrion
    ) -> Dict[str, Any]:
        """Analyze DAG characteristics for performance insights."""
        try:
            characteristics = {
                "task_count": orion.task_count,
                "dependency_count": orion.dependency_count,
                "max_parallel_tasks": len(orion.get_ready_tasks()),
                "critical_path_length": 0,  # Would need graph analysis
                "branching_factor": 0,
                "convergence_points": 0,
                "dag_depth": 0,
            }

            # Calculate some basic metrics
            in_degrees = {}
            out_degrees = {}

            for task_id in orion.tasks.keys():
                in_degrees[task_id] = 0
                out_degrees[task_id] = 0

            for dep in orion.dependencies.values():
                out_degrees[dep.from_task_id] += 1
                in_degrees[dep.to_task_id] += 1

            # Find branching points (tasks with multiple outputs)
            characteristics["branching_factor"] = (
                max(out_degrees.values()) if out_degrees else 0
            )

            # Find convergence points (tasks with multiple inputs)
            characteristics["convergence_points"] = len(
                [task_id for task_id, in_degree in in_degrees.items() if in_degree > 1]
            )

            # Estimate DAG depth (simple approximation)
            try:
                topo_order = orion.get_topological_order()
                characteristics["dag_depth"] = len(topo_order)
            except:
                characteristics["dag_depth"] = orion.task_count

            return characteristics

        except Exception as e:
            logger.warning(f"Could not analyze DAG characteristics: {e}")
            return {"error": str(e)}

    async def test_dag_modifications(
        self, orion: TaskOrion
    ) -> Dict[str, Any]:
        """
        Test dynamic DAG modifications.
        """
        logger.info("\n🔄 Testing DAG Modifications...")

        modification_results = {}

        try:
            # Test 1: Add new task
            logger.info("📝 Test 1: Adding new task...")
            new_task = TaskStar(
                task_id="dynamic_task_1",
                description="Dynamically added monitoring task",
                priority=TaskPriority.MEDIUM,
            )
            orion.add_task(new_task)

            # Add dependency from last task to new task
            tasks = list(orion.tasks.values())
            if len(tasks) > 1:
                last_task = tasks[-2]  # Second to last, since we just added one
                new_dependency = TaskStarLine.create_success_only(
                    last_task.task_id,
                    new_task.task_id,
                    "Dynamic dependency for monitoring",
                )
                orion.add_dependency(new_dependency)

            modification_results["add_task"] = {
                "status": "success",
                "new_task_count": orion.task_count,
                "new_dependency_count": orion.dependency_count,
            }
            logger.info("✅ Successfully added new task and dependency")

            # Test 2: Modify task properties
            logger.info("📝 Test 2: Modifying task properties...")
            if tasks:
                first_task = tasks[0]
                original_priority = first_task.priority
                first_task.priority = TaskPriority.HIGH
                first_task._description += " [MODIFIED]"

                modification_results["modify_task"] = {
                    "status": "success",
                    "original_priority": original_priority.value,
                    "new_priority": first_task.priority.value,
                    "description_modified": True,
                }
                logger.info("✅ Successfully modified task properties")

            # Test 3: Export and import orion
            logger.info("📝 Test 3: Testing export/import...")

            # Export to JSON
            json_export = self.orchestrator.export_orion(orion, "json")

            # Export to LLM format
            llm_export = self.orchestrator.export_orion(orion, "llm")

            # Import from JSON
            imported_orion = self.orchestrator.import_orion(
                json_export, "json"
            )

            modification_results["export_import"] = {
                "status": "success",
                "json_export_length": len(json_export),
                "llm_export_length": len(llm_export),
                "import_task_count": imported_orion.task_count,
                "import_dependency_count": imported_orion.dependency_count,
                "data_integrity": (
                    imported_orion.task_count == orion.task_count
                    and imported_orion.dependency_count
                    == orion.dependency_count
                ),
            }
            logger.info("✅ Successfully exported and imported orion")

            # Test 4: Validate modified DAG
            logger.info("📝 Test 4: Validating modified DAG...")
            is_valid, errors = orion.validate_dag()

            modification_results["validation"] = {
                "status": "success" if is_valid else "failed",
                "is_valid": is_valid,
                "errors": errors,
            }

            if is_valid:
                logger.info("✅ Modified DAG is still valid")
            else:
                logger.warning(f"⚠️ Modified DAG has validation issues: {errors}")

            return modification_results

        except Exception as e:
            logger.error(f"❌ DAG modification test failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "partial_results": modification_results,
            }

    async def test_error_scenarios(self) -> Dict[str, Any]:
        """
        Test error handling and recovery scenarios.
        """
        logger.info("\n⚠️ Testing Error Scenarios...")

        error_test_results = {}

        try:
            # Test 1: Invalid LLM input
            logger.info("📝 Test 1: Invalid LLM input...")
            try:
                invalid_llm = "This is not a valid task description with no structure"
                orion = await self.orchestrator.create_orion_from_llm(
                    invalid_llm, "invalid_test"
                )
                error_test_results["invalid_llm"] = {
                    "status": "unexpected_success",
                    "tasks_created": orion.task_count,
                }
            except Exception as e:
                error_test_results["invalid_llm"] = {
                    "status": "expected_failure",
                    "error": str(e),
                }
                logger.info("✅ Invalid LLM input correctly rejected")

            # Test 2: Circular dependency
            logger.info("📝 Test 2: Circular dependency detection...")
            try:
                orion = TaskOrion(name="circular_test")

                task_a = TaskStar(task_id="task_a", description="Task A")
                task_b = TaskStar(task_id="task_b", description="Task B")
                task_c = TaskStar(task_id="task_c", description="Task C")

                orion.add_task(task_a)
                orion.add_task(task_b)
                orion.add_task(task_c)

                # Create circular dependency: A -> B -> C -> A
                dep1 = TaskStarLine.create_unconditional("task_a", "task_b", "A to B")
                dep2 = TaskStarLine.create_unconditional("task_b", "task_c", "B to C")
                dep3 = TaskStarLine.create_unconditional(
                    "task_c", "task_a", "C to A (circular)"
                )

                orion.add_dependency(dep1)
                orion.add_dependency(dep2)
                orion.add_dependency(dep3)  # This should fail

                error_test_results["circular_dependency"] = {
                    "status": "unexpected_success",
                    "message": "Circular dependency was allowed",
                }

            except Exception as e:
                error_test_results["circular_dependency"] = {
                    "status": "expected_failure",
                    "error": str(e),
                }
                logger.info("✅ Circular dependency correctly detected and prevented")

            # Test 3: Device failure simulation
            logger.info("📝 Test 3: Device failure handling...")
            # Create a simple orion for failure testing
            simple_orion = create_simple_orion(
                ["Task that might fail", "Recovery task"],
                "failure_test",
                sequential=True,
            )

            await self.orchestrator.assign_devices_automatically(simple_orion)

            # Simulate device disconnection
            original_devices = self.mock_client.connected_devices.copy()
            device_to_disconnect = list(self.mock_client.connected_devices.keys())[0]
            self.mock_client.connected_devices[device_to_disconnect][
                "status"
            ] = "disconnected"

            try:
                result = await self.orchestrator.orchestrate_orion(
                    simple_orion
                )
                error_test_results["device_failure"] = {
                    "status": "handled",
                    "execution_result": result.get("status"),
                    "message": "Orion execution completed despite device failure",
                }
            except Exception as e:
                error_test_results["device_failure"] = {
                    "status": "failed",
                    "error": str(e),
                }
            finally:
                # Restore device state
                self.mock_client.connected_devices = original_devices

            logger.info("✅ Device failure scenario tested")

            return error_test_results

        except Exception as e:
            logger.error(f"❌ Error scenario testing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "partial_results": error_test_results,
            }

    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """
        Run the complete end-to-end test suite.
        """
        logger.info("🚀 Starting Comprehensive E2E Test Suite")
        logger.info("=" * 80)

        suite_start_time = time.time()
        suite_results = {
            "test_suite_start": datetime.now().isoformat(),
            "dag_structure_tests": {},
            "modification_tests": {},
            "error_scenario_tests": {},
            "performance_summary": {},
            "overall_status": "running",
        }

        try:
            # Phase 1: Test different DAG structures
            logger.info("\n🏗️ PHASE 1: DAG Structure Testing")
            logger.info("-" * 50)

            llm_responses = self.create_mock_llm_responses()

            for dag_name, llm_response in llm_responses.items():
                try:
                    test_result = await self.test_dag_structure(dag_name, llm_response)
                    suite_results["dag_structure_tests"][dag_name] = test_result

                    # Reset mock client state between tests
                    self.mock_client.task_execution_log = []
                    for device_id in self.mock_client.connected_devices:
                        self.mock_client.connected_devices[device_id]["load"] = 0.1

                except Exception as e:
                    logger.error(f"Failed testing {dag_name}: {e}")
                    suite_results["dag_structure_tests"][dag_name] = {
                        "status": "failed",
                        "error": str(e),
                    }

            # Phase 2: Test DAG modifications (using the last successful orion)
            logger.info("\n🔄 PHASE 2: DAG Modification Testing")
            logger.info("-" * 50)

            # Find a successful orion to modify
            successful_orion = None
            for dag_name, result in suite_results["dag_structure_tests"].items():
                if result.get("status") == "completed":
                    # Recreate orion for modification testing
                    llm_response = llm_responses.get(dag_name)
                    if llm_response:
                        successful_orion = (
                            await self.orchestrator.create_orion_from_llm(
                                llm_response, f"{dag_name}_for_modification"
                            )
                        )
                        break

            if successful_orion:
                modification_results = await self.test_dag_modifications(
                    successful_orion
                )
                suite_results["modification_tests"] = modification_results
            else:
                suite_results["modification_tests"] = {
                    "status": "skipped",
                    "reason": "No successful orion available for modification testing",
                }

            # Phase 3: Test error scenarios
            logger.info("\n⚠️ PHASE 3: Error Scenario Testing")
            logger.info("-" * 50)

            error_results = await self.test_error_scenarios()
            suite_results["error_scenario_tests"] = error_results

            # Phase 4: Generate performance summary
            logger.info("\n📊 PHASE 4: Performance Analysis")
            logger.info("-" * 50)

            suite_results["performance_summary"] = self._generate_performance_summary(
                suite_results
            )

            suite_end_time = time.time()
            suite_results["total_execution_time"] = suite_end_time - suite_start_time
            suite_results["test_suite_end"] = datetime.now().isoformat()
            suite_results["overall_status"] = "completed"

            # Final summary
            self._print_final_summary(suite_results)

            return suite_results

        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            logger.error(traceback.format_exc())

            suite_results["overall_status"] = "failed"
            suite_results["error"] = str(e)
            suite_results["total_execution_time"] = time.time() - suite_start_time

            return suite_results

    def _generate_performance_summary(
        self, suite_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate performance analysis summary."""
        dag_tests = suite_results.get("dag_structure_tests", {})

        if not dag_tests:
            return {"status": "no_data"}

        # Collect performance metrics
        execution_times = []
        task_counts = []
        dependency_counts = []
        success_rates = []

        for dag_name, result in dag_tests.items():
            if result.get("status") == "completed":
                execution_times.append(result.get("total_execution_time", 0))

                stats = result.get("orion_stats", {})
                task_counts.append(stats.get("total_tasks", 0))
                dependency_counts.append(stats.get("total_dependencies", 0))

                completed_tasks = len(result.get("task_results", {}))
                total_tasks = stats.get("total_tasks", 1)
                success_rates.append(
                    completed_tasks / total_tasks if total_tasks > 0 else 0
                )

        if not execution_times:
            return {"status": "no_successful_tests"}

        return {
            "status": "completed",
            "test_count": len(dag_tests),
            "successful_tests": len(execution_times),
            "success_rate": len(execution_times) / len(dag_tests),
            "performance_metrics": {
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "avg_task_count": (
                    sum(task_counts) / len(task_counts) if task_counts else 0
                ),
                "avg_dependency_count": (
                    sum(dependency_counts) / len(dependency_counts)
                    if dependency_counts
                    else 0
                ),
                "avg_task_success_rate": (
                    sum(success_rates) / len(success_rates) if success_rates else 0
                ),
            },
            "device_performance": self._analyze_overall_device_performance(),
        }

    def _analyze_overall_device_performance(self) -> Dict[str, Any]:
        """Analyze overall device performance across all tests."""
        return {
            "total_tasks_executed": len(self.mock_client.task_execution_log),
            "device_utilization": self._analyze_device_utilization(),
            "average_task_execution_time": (
                (
                    sum(
                        [
                            log["execution_time"]
                            for log in self.mock_client.task_execution_log
                        ]
                    )
                    / len(self.mock_client.task_execution_log)
                )
                if self.mock_client.task_execution_log
                else 0
            ),
        }

    def _print_final_summary(self, suite_results: Dict[str, Any]):
        """Print comprehensive test suite summary."""
        logger.info("\n" + "🎯" * 30)
        logger.info("  COMPREHENSIVE TEST SUITE SUMMARY")
        logger.info("🎯" * 30)

        # Overall statistics
        total_time = suite_results.get("total_execution_time", 0)
        logger.info(f"\n📊 Overall Statistics:")
        logger.info(f"   - Total execution time: {total_time:.2f}s")
        logger.info(f"   - Test suite status: {suite_results.get('overall_status')}")

        # DAG structure test results
        dag_tests = suite_results.get("dag_structure_tests", {})
        logger.info(f"\n🏗️ DAG Structure Tests ({len(dag_tests)} total):")
        for dag_name, result in dag_tests.items():
            status = result.get("status", "unknown")
            execution_time = result.get("total_execution_time", 0)
            logger.info(f"   - {dag_name}: {status} ({execution_time:.2f}s)")

        # Performance summary
        perf_summary = suite_results.get("performance_summary", {})
        if perf_summary.get("status") == "completed":
            metrics = perf_summary.get("performance_metrics", {})
            logger.info(f"\n📈 Performance Metrics:")
            logger.info(f"   - Success rate: {perf_summary.get('success_rate', 0):.1%}")
            logger.info(
                f"   - Avg execution time: {metrics.get('avg_execution_time', 0):.2f}s"
            )
            logger.info(f"   - Avg task count: {metrics.get('avg_task_count', 0):.1f}")
            logger.info(
                f"   - Avg dependency count: {metrics.get('avg_dependency_count', 0):.1f}"
            )

        # Device performance
        device_perf = perf_summary.get("device_performance", {})
        logger.info(f"\n💻 Device Performance:")
        logger.info(
            f"   - Total tasks executed: {device_perf.get('total_tasks_executed', 0)}"
        )
        logger.info(
            f"   - Avg task execution time: {device_perf.get('average_task_execution_time', 0):.2f}s"
        )

        # Error scenarios
        error_tests = suite_results.get("error_scenario_tests", {})
        logger.info(f"\n⚠️ Error Scenario Tests:")
        if error_tests:
            for test_name, result in error_tests.items():
                if isinstance(result, dict):
                    status = result.get("status", "unknown")
                    logger.info(f"   - {test_name}: {status}")

        logger.info(f"\n✅ Test suite completed successfully!")
        logger.info("🎯" * 30)


class NetworkSessionTester:
    """
    Comprehensive tester for NetworkSession and NetworkWeaverAgent integration.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def test_network_session_lifecycle(self) -> Dict[str, Any]:
        """Test complete NetworkSession lifecycle with NetworkWeaverAgent."""
        self.logger.info("\n🌌 Testing NetworkSession Lifecycle...")

        results = {
            "test_name": "network_session_lifecycle",
            "status": "unknown",
            "start_time": time.time(),
            "tests": {},
        }

        try:
            # Test 1: Session Creation
            self.logger.info("📝 Test 1: Session creation and initialization...")

            # Create modular client
            config = OrionConfig()
            client = OrionClient(config)

            # Create mock weaver agent
            weaver_agent = MockNetworkWeaverAgent("test_weaver")

            # Create network session
            session = NetworkSession(
                task="test_network_workflow",
                should_evaluate=False,
                id="network_test_001",
                agent=weaver_agent,
                client=client,
                initial_request="Create a comprehensive data analysis workflow with parallel processing",
            )

            results["tests"]["session_creation"] = {
                "status": "success",
                "agent_type": type(session.weaver_agent).__name__,
                "session_id": session.id,
            }

            # Test 2: Agent Initial Processing
            self.logger.info("📝 Test 2: Agent initial request processing...")

            orion = await weaver_agent.process_initial_request(
                "Create a machine learning pipeline with data preprocessing, training, and evaluation",
                session.context,
            )

            results["tests"]["initial_processing"] = {
                "status": "success",
                "orion_id": orion.orion_id,
                "task_count": orion.task_count,
                "agent_status": weaver_agent.agent_status,
            }

            # Test 3: Session Execution
            self.logger.info("📝 Test 3: Full session execution...")

            # Run session (this will create rounds and execute orion)
            session_start = time.time()
            await session.run()
            execution_time = time.time() - session_start

            # Get final status
            final_status = await session.get_session_status()

            results["tests"]["session_execution"] = {
                "status": "success",
                "execution_time": execution_time,
                "rounds_completed": final_status["rounds_completed"],
                "final_agent_status": final_status["agent_status"],
                "orion_stats": final_status.get("orion_stats", {}),
            }

            # Test 4: Task Result Processing
            self.logger.info("📝 Test 4: Task result processing and DAG updates...")

            # Simulate task results for testing agent updates
            mock_task_result = {
                "task_id": "test_task_001",
                "status": "completed",
                "result": {
                    "output": "Analysis completed successfully",
                    "metrics": {"accuracy": 0.95},
                },
                "timestamp": time.time(),
            }

            # Test agent's task result processing
            if session.current_orion:
                updated_orion = (
                    await weaver_agent.update_orion_with_lock(
                        mock_task_result, session.context
                    )
                )

                results["tests"]["task_result_processing"] = {
                    "status": "success",
                    "original_task_count": orion.task_count,
                    "updated_task_count": updated_orion.task_count,
                    "agent_status_after_update": weaver_agent.agent_status,
                }

            # Test 5: Error Handling
            self.logger.info("📝 Test 5: Error handling and recovery...")

            # Simulate error scenario
            error_task_result = {
                "task_id": "test_error_task",
                "status": "failed",
                "result": {
                    "error": "Simulated task failure",
                    "error_code": "TASK_ERROR",
                },
                "timestamp": time.time(),
            }

            try:
                await weaver_agent.update_orion_with_lock(
                    error_task_result, session.context
                )

                results["tests"]["error_handling"] = {
                    "status": "success",
                    "error_processed": True,
                    "agent_status": weaver_agent.agent_status,
                }
            except Exception as e:
                results["tests"]["error_handling"] = {
                    "status": "handled_error",
                    "error": str(e),
                }

            results["status"] = "success"
            results["total_execution_time"] = time.time() - results["start_time"]

            self.logger.info("✅ NetworkSession lifecycle test completed successfully")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["total_execution_time"] = time.time() - results["start_time"]
            self.logger.error(f"❌ NetworkSession lifecycle test failed: {e}")
            import traceback

            traceback.print_exc()

        return results

    async def test_weaver_agent_scenarios(self) -> Dict[str, Any]:
        """Test various NetworkWeaverAgent scenarios."""
        self.logger.info("\n🤖 Testing NetworkWeaverAgent Scenarios...")

        results = {
            "test_name": "weaver_agent_scenarios",
            "status": "unknown",
            "start_time": time.time(),
            "scenarios": {},
        }

        try:
            # Scenario 1: Complex Request Processing
            self.logger.info("📝 Scenario 1: Complex request processing...")

            agent = MockNetworkWeaverAgent("scenario_agent_1")
            complex_request = "Build a complex distributed system with microservices, load balancing, monitoring, and CI/CD pipeline"

            orion = await agent.process_initial_request(complex_request)

            results["scenarios"]["complex_request"] = {
                "status": "success",
                "request_length": len(complex_request),
                "generated_tasks": orion.task_count,
                "orion_state": orion.state.value,
                "agent_status": agent.agent_status,
            }

            # Scenario 2: Parallel Processing Request
            self.logger.info("📝 Scenario 2: Parallel processing request...")

            agent2 = MockNetworkWeaverAgent("scenario_agent_2")
            parallel_request = "Create a parallel data processing system with multiple data streams and aggregation"

            orion2 = await agent2.process_initial_request(parallel_request)

            results["scenarios"]["parallel_request"] = {
                "status": "success",
                "request_type": "parallel",
                "generated_tasks": orion2.task_count,
                "agent_status": agent2.agent_status,
            }

            # Scenario 3: Agent State Management
            self.logger.info("📝 Scenario 3: Agent state management...")

            # Test status transitions
            initial_status = agent.agent_status

            # Simulate completion
            completion_result = {
                "task_id": "final_task",
                "status": "completed",
                "result": {"summary": "All tasks completed successfully"},
            }

            # Process result and check status change
            await agent.update_orion_with_lock(completion_result)
            final_status = agent.agent_status

            results["scenarios"]["state_management"] = {
                "status": "success",
                "initial_status": initial_status,
                "final_status": final_status,
                "status_changed": initial_status != final_status,
            }

            # Scenario 4: Concurrent Updates
            self.logger.info("📝 Scenario 4: Concurrent update handling...")

            agent3 = MockNetworkWeaverAgent("scenario_agent_3")
            await agent3.process_initial_request("Simple linear workflow")

            # Simulate concurrent updates
            update_tasks = []
            for i in range(3):
                task_result = {
                    "task_id": f"concurrent_task_{i}",
                    "status": "completed",
                    "result": {"data": f"Result {i}"},
                }
                update_tasks.append(agent3.update_orion_with_lock(task_result))

            # Wait for all updates
            await asyncio.gather(*update_tasks)

            results["scenarios"]["concurrent_updates"] = {
                "status": "success",
                "concurrent_updates": len(update_tasks),
                "final_agent_status": agent3.agent_status,
            }

            results["status"] = "success"
            results["total_execution_time"] = time.time() - results["start_time"]

            self.logger.info(
                "✅ NetworkWeaverAgent scenarios test completed successfully"
            )

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["total_execution_time"] = time.time() - results["start_time"]
            self.logger.error(f"❌ NetworkWeaverAgent scenarios test failed: {e}")
            import traceback

            traceback.print_exc()

        return results

    async def test_session_agent_integration(self) -> Dict[str, Any]:
        """Test integration between NetworkSession and NetworkWeaverAgent."""
        self.logger.info("\n🔗 Testing Session-Agent Integration...")

        results = {
            "test_name": "session_agent_integration",
            "status": "unknown",
            "start_time": time.time(),
            "integration_tests": {},
        }

        try:
            # Integration Test 1: End-to-End Request Processing
            self.logger.info("📝 Integration Test 1: End-to-end request processing...")

            # Create session with custom agent
            agent = MockNetworkWeaverAgent("integration_agent")
            config = OrionConfig()
            client = OrionClient(config)

            session = NetworkSession(
                task="integration_test",
                should_evaluate=False,
                id="integration_001",
                agent=agent,
                client=client,
                initial_request="Create an automated testing framework with parallel test execution",
            )

            # Execute session and track agent state changes
            initial_agent_status = agent.agent_status
            await session.run()
            final_agent_status = agent.agent_status

            session_status = await session.get_session_status()

            results["integration_tests"]["end_to_end"] = {
                "status": "success",
                "initial_agent_status": initial_agent_status,
                "final_agent_status": final_agent_status,
                "session_rounds": session_status["rounds_completed"],
                "orion_created": session.current_orion is not None,
            }

            # Integration Test 2: Real-time DAG Updates
            self.logger.info(
                "📝 Integration Test 2: Real-time DAG updates during execution..."
            )

            if session.current_orion:
                original_task_count = session.current_orion.task_count

                # Simulate task completion that should trigger updates
                mock_result = {
                    "task_id": "trigger_task",
                    "status": "completed",
                    "result": {"needs_additional_processing": True},
                }

                await agent.update_orion_with_lock(mock_result, session.context)

                updated_task_count = session.current_orion.task_count

                results["integration_tests"]["realtime_updates"] = {
                    "status": "success",
                    "original_task_count": original_task_count,
                    "updated_task_count": updated_task_count,
                    "tasks_added": updated_task_count > original_task_count,
                }

            # Integration Test 3: Session Termination Scenarios
            self.logger.info("📝 Integration Test 3: Session termination scenarios...")

            # Test force finish
            await session.force_finish("Integration test completion")

            final_session_status = await session.get_session_status()

            results["integration_tests"]["termination"] = {
                "status": "success",
                "forced_finish": True,
                "final_agent_status": agent.agent_status,
                "session_finished": session.is_finished(),
            }

            results["status"] = "success"
            results["total_execution_time"] = time.time() - results["start_time"]

            self.logger.info("✅ Session-Agent integration test completed successfully")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["total_execution_time"] = time.time() - results["start_time"]
            self.logger.error(f"❌ Session-Agent integration test failed: {e}")
            import traceback

            traceback.print_exc()

        return results

    async def test_dynamic_dag_execution_flow(self) -> Dict[str, Any]:
        """
        Test the complete dynamic DAG execution flow:
        1. Initial DAG execution
        2. Task completion triggers agent processing
        3. Agent dynamically adds new tasks based on results
        4. Subsequent tasks are executed automatically
        5. Multi-round updates and execution
        """
        self.logger.info("\n🔄 Testing Dynamic DAG Execution Flow...")

        results = {
            "test_name": "dynamic_dag_execution_flow",
            "status": "unknown",
            "start_time": time.time(),
            "execution_phases": {},
        }

        try:
            # Phase 1: Initial DAG Creation and Execution
            self.logger.info(
                "📝 Phase 1: Creating initial DAG with conditional logic..."
            )

            # Create a session with dynamic workflow
            agent = MockNetworkWeaverAgent("dynamic_agent")
            config = OrionConfig()
            client = OrionClient(config)

            session = NetworkSession(
                task="dynamic_flow_test",
                should_evaluate=False,
                id="dynamic_001",
                agent=agent,
                client=client,
                initial_request="Analyze data and create adaptive machine learning pipeline based on data characteristics",
            )

            # Run initial session to create orion
            await session.run()
            initial_orion = session.current_orion

            if not initial_orion:
                raise Exception("Failed to create initial orion")

            self.logger.info(
                f"Initial orion created with {initial_orion.task_count} tasks"
            )

            results["execution_phases"]["initial_creation"] = {
                "status": "success",
                "initial_task_count": initial_orion.task_count,
                "orion_id": initial_orion.orion_id,
            }

            # Phase 2: Simulate Multi-Round Task Execution with Dynamic Updates
            self.logger.info(
                "📝 Phase 2: Simulating multi-round execution with dynamic updates..."
            )

            execution_round = 1
            total_phases = 3
            orion = initial_orion

            for phase in range(total_phases):
                self.logger.info(f"   --- Execution Round {execution_round} ---")

                # Simulate completing tasks with different result types
                available_task_ids = list(orion.tasks.keys())
                if not available_task_ids:
                    self.logger.info("No more tasks available, breaking execution loop")
                    break

                # Select first available task for simulation
                task_id = available_task_ids[0]
                completed_task = orion.tasks[task_id]

                # Create result based on task content and execution round
                if execution_round == 1:
                    # First round: Data analysis completion triggers model selection
                    task_result = {
                        "task_id": task_id,
                        "status": "completed",
                        "result": {
                            "data_analysis": {
                                "data_type": "time_series",
                                "data_size": "large",
                                "complexity": "high",
                                "patterns_found": ["seasonality", "trend", "anomalies"],
                            },
                            "recommendations": [
                                "use_deep_learning",
                                "add_feature_engineering",
                                "include_anomaly_detection",
                            ],
                            "trigger_tasks": [
                                "advanced_feature_engineering",
                                "deep_learning_model_selection",
                                "anomaly_detection_setup",
                            ],
                        },
                        "timestamp": time.time(),
                    }
                elif execution_round == 2:
                    # Second round: Model training completion triggers evaluation
                    task_result = {
                        "task_id": task_id,
                        "status": "completed",
                        "result": {
                            "model_training": {
                                "model_type": "lstm",
                                "training_accuracy": 0.92,
                                "validation_accuracy": 0.87,
                                "training_time": "45_minutes",
                            },
                            "performance_metrics": {
                                "accuracy": 0.87,
                                "precision": 0.89,
                                "recall": 0.85,
                                "f1_score": 0.87,
                            },
                            "recommendations": [
                                "perform_cross_validation",
                                "try_ensemble_methods",
                                "tune_hyperparameters",
                            ],
                            "trigger_tasks": [
                                "cross_validation_testing",
                                "ensemble_model_creation",
                                "hyperparameter_optimization",
                            ],
                        },
                        "timestamp": time.time(),
                    }
                else:
                    # Third round: Final optimization
                    task_result = {
                        "task_id": task_id,
                        "status": "completed",
                        "result": {
                            "optimization": {
                                "method": "grid_search",
                                "best_params": {"lr": 0.001, "batch_size": 64},
                                "final_accuracy": 0.94,
                                "improvement": 0.07,
                            },
                            "deployment_ready": True,
                            "trigger_tasks": [
                                "model_deployment_prep",
                                "monitoring_setup",
                            ],
                        },
                        "timestamp": time.time(),
                    }

                self.logger.info(f"Simulating completion of task: {task_id}")
                self.logger.info(
                    f"Result contains: {list(task_result['result'].keys())}"
                )

                # Phase 3: Agent Processes Result and Updates DAG
                self.logger.info(
                    "📝 Phase 3: Agent processing result and updating DAG..."
                )

                previous_task_count = orion.task_count

                # Agent processes the result and potentially adds new tasks
                updated_orion = await agent.update_orion_with_lock(
                    task_result, session.context
                )

                new_task_count = (
                    updated_orion.task_count
                    if updated_orion
                    else previous_task_count
                )
                tasks_added = new_task_count - previous_task_count

                self.logger.info(
                    f"Tasks before: {previous_task_count}, after: {new_task_count}, added: {tasks_added}"
                )

                # Update orion reference
                if updated_orion:
                    orion = updated_orion
                    session._orion = updated_orion

                results["execution_phases"][f"round_{execution_round}"] = {
                    "status": "success",
                    "completed_task_id": task_id,
                    "completed_task_type": (
                        completed_task.description[:50] + "..."
                        if len(completed_task.description) > 50
                        else completed_task.description
                    ),
                    "result_summary": {
                        k: str(v)[:100] for k, v in task_result["result"].items()
                    },
                    "tasks_before_update": previous_task_count,
                    "tasks_after_update": new_task_count,
                    "new_tasks_added": tasks_added,
                    "agent_status": agent.agent_status,
                }

                # Phase 4: Simulate Execution of New Tasks (if any)
                if tasks_added > 0:
                    self.logger.info(
                        f"📝 Phase 4: Simulating execution of {tasks_added} new tasks..."
                    )

                    # Simulate execution of a couple of newly added tasks
                    all_task_ids = list(orion.tasks.keys())
                    newer_tasks = [
                        tid for tid in all_task_ids if tid != task_id
                    ]  # Exclude the just completed task

                    for i, new_task_id in enumerate(
                        newer_tasks[:2]
                    ):  # Execute up to 2 new tasks
                        new_task = orion.tasks[new_task_id]
                        new_task_result = {
                            "task_id": new_task_id,
                            "status": "completed",
                            "result": {
                                "sub_task_output": f"Successfully completed {new_task.description[:30]}",
                                "generated_in_round": execution_round,
                                "execution_order": i + 1,
                                "contributes_to": "overall_pipeline_improvement",
                            },
                            "timestamp": time.time(),
                        }

                        self.logger.info(f"Executing new task: {new_task_id}")

                        # Process the new task result (might add more tasks)
                        further_updated = await agent.update_orion_with_lock(
                            new_task_result, session.context
                        )

                        if further_updated:
                            orion = further_updated

                execution_round += 1

                # Prevent infinite loop
                if execution_round > 5:
                    self.logger.info("Reached maximum execution rounds, stopping")
                    break

            # Phase 5: Final State Analysis
            self.logger.info("📝 Phase 5: Analyzing final DAG state...")

            final_stats = orion.get_statistics() if orion else {}
            final_task_count = orion.task_count if orion else 0

            results["execution_phases"]["final_analysis"] = {
                "status": "success",
                "final_task_count": final_task_count,
                "total_rounds": execution_round - 1,
                "final_orion_state": (
                    orion.state.value if orion else "unknown"
                ),
                "final_statistics": final_stats,
                "agent_final_status": agent.agent_status,
            }

            # Summary
            initial_count = results["execution_phases"]["initial_creation"][
                "initial_task_count"
            ]
            total_added = final_task_count - initial_count

            self.logger.info(f"🎯 Dynamic DAG Execution Summary:")
            self.logger.info(f"   - Initial tasks: {initial_count}")
            self.logger.info(f"   - Final tasks: {final_task_count}")
            self.logger.info(f"   - Tasks dynamically added: {total_added}")
            self.logger.info(f"   - Execution rounds: {execution_round - 1}")
            self.logger.info(
                f"   - Final state: {orion.state.value if orion else 'N/A'}"
            )

            results["status"] = "success"
            results["summary"] = {
                "initial_task_count": initial_count,
                "final_task_count": final_task_count,
                "total_tasks_added": total_added,
                "execution_rounds": execution_round - 1,
                "success_rate": 1.0,
            }

            self.logger.info(
                "✅ Dynamic DAG execution flow test completed successfully"
            )

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            self.logger.error(f"❌ Dynamic DAG execution flow test failed: {e}")
            import traceback

            traceback.print_exc()

        finally:
            results["total_execution_time"] = time.time() - results["start_time"]

        return results

    async def run_network_tests(self) -> Dict[str, Any]:
        """Run all Network framework tests."""
        self.logger.info("\n🌌🌌🌌 NETWORK FRAMEWORK INTEGRATION TESTS 🌌🌌🌌")

        network_results = {
            "network_test_suite": "complete",
            "start_time": time.time(),
            "tests": {},
        }

        # Run all test categories
        network_results["tests"][
            "session_lifecycle"
        ] = await self.test_network_session_lifecycle()
        network_results["tests"][
            "weaver_scenarios"
        ] = await self.test_weaver_agent_scenarios()
        network_results["tests"][
            "integration"
        ] = await self.test_session_agent_integration()
        network_results["tests"][
            "dynamic_dag_execution"
        ] = await self.test_dynamic_dag_execution_flow()

        # Calculate overall results
        total_time = time.time() - network_results["start_time"]
        successful_tests = sum(
            1
            for test in network_results["tests"].values()
            if test.get("status") == "success"
        )
        total_tests = len(network_results["tests"])

        network_results.update(
            {
                "total_execution_time": total_time,
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "success_rate": (
                    successful_tests / total_tests if total_tests > 0 else 0
                ),
                "overall_status": (
                    "success" if successful_tests == total_tests else "partial_success"
                ),
            }
        )

        self.logger.info(f"\n🌌 Network Framework Test Summary:")
        self.logger.info(f"   - Total tests: {total_tests}")
        self.logger.info(f"   - Successful: {successful_tests}")
        self.logger.info(f"   - Success rate: {network_results['success_rate']:.1%}")
        self.logger.info(f"   - Total time: {total_time:.2f}s")

        return network_results


async def main():
    """
    Main function to run the comprehensive E2E test suite including Network framework tests.
    """
    print("🌟" * 40)
    print("  End-to-End TaskOrion Test Suite")
    print("  Network Framework Integration Test")
    print("🌟" * 40)

    print(f"\n📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Test Environment: Mock Network Framework")
    print(
        "📋 Test Coverage: LLM Parsing → DAG Creation → Device Assignment → Execution → Updates → Network Sessions"
    )

    try:
        # Initialize the comprehensive tester
        tester = E2EOrionTester()
        network_tester = NetworkSessionTester()

        # Run the original orion test suite
        orion_results = await tester.run_comprehensive_test_suite()

        # Run the Network framework tests
        network_results = await network_tester.run_network_tests()

        # Combine results
        combined_results = {
            "test_suite": "comprehensive_e2e_with_network",
            "orion_tests": orion_results,
            "network_tests": network_results,
            "overall_summary": {
                "orion_success": orion_results.get("overall_status")
                == "completed",
                "network_success": network_results.get("overall_status")
                in ["success", "partial_success"],
                "total_execution_time": (
                    orion_results.get("total_execution_time", 0)
                    + network_results.get("total_execution_time", 0)
                ),
            },
        }

        # Save results to file for analysis
        results_file = (
            f"e2e_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(combined_results, f, indent=2, default=str)

        print(f"\n💾 Test results saved to: {results_file}")

        # Print combined summary
        print(f"\n🎯 OVERALL TEST SUITE SUMMARY:")
        print(
            f"   - Orion Tests: {'✅ SUCCESS' if combined_results['overall_summary']['orion_success'] else '❌ FAILED'}"
        )
        print(
            f"   - Network Framework Tests: {'✅ SUCCESS' if combined_results['overall_summary']['network_success'] else '❌ FAILED'}"
        )
        print(
            f"   - Total Execution Time: {combined_results['overall_summary']['total_execution_time']:.2f}s"
        )

        # Return combined results for further analysis
        return combined_results

    except Exception as e:
        logger.error(f"❌ Test suite execution failed: {e}")
        logger.error(traceback.format_exc())
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    # Run the comprehensive E2E test suite with Network framework
    results = asyncio.run(main())

    # Exit with appropriate code
    overall_success = results.get("overall_summary", {}).get(
        "orion_success", False
    ) and results.get("overall_summary", {}).get("network_success", False)

    if overall_success:
        exit(0)
    else:
        exit(1)
        exit(1)
