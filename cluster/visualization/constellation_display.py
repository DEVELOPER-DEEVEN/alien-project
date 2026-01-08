# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
network-specific visualization display components.

This module provides specialized display functionality for network-related
visualizations with rich console output, including structure changes,
statistics, and state transitions.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from ..network.task_network import Tasknetwork

from ..network.enums import networkState


class networkDisplay:
    """
    Specialized display components for network visualization.

    Provides reusable, modular components for displaying network information
    with consistent Rich formatting across different contexts.
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize networkDisplay.

        :param console: Optional Rich Console instance for output
        """
        self.console = console or Console()

    def display_network_started(
        self,
        network: "Tasknetwork",
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display network start notification.

        :param network: Tasknetwork that started
        :param additional_info: Optional additional information
        """
        # Create network info
        info_panel = self._create_basic_info_panel(
            network, "🚀 network Started", additional_info
        )

        # Create basic stats
        stats_panel = self._create_basic_stats_panel(network)

        # Display side by side
        self.console.print()
        self.console.rule("[bold cyan]🚀 network Started[/bold cyan]")
        self.console.print(Columns([info_panel, stats_panel], equal=True))

    def display_network_completed(
        self,
        network: "Tasknetwork",
        execution_time: Optional[float] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display network completion notification with enhanced formatting.

        :param network: Tasknetwork that completed
        :param execution_time: Total execution time in seconds
        :param additional_info: Optional additional information
        """
        from .network_formatter import networkFormatter

        # Prepare data for the formatter
        stats = (
            network.get_statistics()
            if hasattr(network, "get_statistics")
            else {}
        )

        network_data = {
            "id": network.network_id,
            "name": network.name or network.network_id,
            "state": (
                network.state.value
                if hasattr(network.state, "value")
                else str(network.state)
            ),
            "total_tasks": (
                len(network.tasks) if hasattr(network, "tasks") else 0
            ),
            "execution_duration": execution_time or 0,
            "statistics": stats,
            "network": str(network),
        }

        # Add timing information if available
        if hasattr(network, "created_at") and network.created_at:
            network_data["created"] = network.created_at.strftime(
                "%H:%M:%S"
            )

        if (
            hasattr(network, "execution_start_time")
            and network.execution_start_time
        ):
            network_data["started"] = network.execution_start_time.strftime(
                "%H:%M:%S"
            )

        if (
            hasattr(network, "execution_end_time")
            and network.execution_end_time
        ):
            network_data["ended"] = network.execution_end_time.strftime(
                "%H:%M:%S"
            )

        # Merge additional info
        if additional_info:
            network_data.update(additional_info)

        # Use the new formatter to display
        formatter = networkFormatter()
        formatter.display_network_result(network_data)

    def display_network_failed(
        self,
        network: "Tasknetwork",
        error: Optional[Exception] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display network failure notification.

        :param network: Tasknetwork that failed
        :param error: Exception that caused the failure
        :param additional_info: Optional additional information
        """
        # Enhance additional info with error
        enhanced_info = additional_info.copy() if additional_info else {}
        if error:
            enhanced_info["error"] = str(error)[:100]

        # Create failure info
        info_panel = self._create_basic_info_panel(
            network, "❌ network Failed", enhanced_info
        )

        # Create stats with failure emphasis
        stats_panel = self._create_basic_stats_panel(network)

        # Display with error styling
        self.console.print()
        self.console.rule("[bold red]❌ network Failed[/bold red]")
        self.console.print(Columns([info_panel, stats_panel], equal=True))

    def display_network_modified(
        self,
        network: "Tasknetwork",
        changes: Dict[str, Any],
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display network modification notification with change details.

        :param network: Modified Tasknetwork
        :param changes: Dictionary containing detected changes
        :param additional_info: Optional additional information
        """
        # Create modification message
        mod_text = Text()
        mod_text.append("🔄 ", style="bold blue")
        mod_text.append(f"network Modified: ", style="bold blue")
        mod_text.append(f"{network.name}", style="bold yellow")
        mod_text.append(f" ({network.network_id[:8]}...)", style="dim")

        # Create details table for changes
        table = Table(show_header=False, show_edge=False, padding=0)
        table.add_column("Key", style="cyan", width=20)
        table.add_column(
            "Value", width=50
        )  # Remove default white style to allow individual coloring

        # Add calculated modification details
        if changes.get("modification_type"):
            mod_type = changes["modification_type"].replace("_", " ").title()
            table.add_row("🔧 Change Type:", f"[bold blue]{mod_type}[/bold blue]")

        self._add_change_details_to_table(table, changes)
        self._add_network_stats_to_table(table, network)

        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if value is not None:
                    table.add_row(f"ℹ️ {key.title()}:", f"[cyan]{value}[/cyan]")

        # Create panel with proper Rich composition
        content = Group(mod_text, "", table)

        panel = Panel(
            content,
            title="[bold blue]⚙️ network Structure Updated[/bold blue]",
            border_style="blue",
            width=80,
        )

        self.console.print(panel)

    def _create_basic_info_panel(
        self,
        network: "Tasknetwork",
        title: str,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Panel:
        """
        Create basic network information panel.

        :param network: Tasknetwork to display info for
        :param title: Panel title
        :param additional_info: Optional additional information
        :return: Rich Panel with network information
        """
        info_lines = [
            f"[bold]ID:[/bold] {network.network_id[:12]}...",
            f"[bold]Name:[/bold] {network.name or 'Unnamed'}",
            f"[bold]State:[/bold] {self._get_state_text(network.state)}",
        ]

        # Add timing information if available
        if hasattr(network, "created_at") and network.created_at:
            info_lines.append(
                f"[bold]Created:[/bold] {network.created_at.strftime('%H:%M:%S')}"
            )

        if (
            hasattr(network, "execution_start_time")
            and network.execution_start_time
        ):
            info_lines.append(
                f"[bold]Started:[/bold] {network.execution_start_time.strftime('%H:%M:%S')}"
            )

        if (
            hasattr(network, "execution_end_time")
            and network.execution_end_time
        ):
            info_lines.append(
                f"[bold]Ended:[/bold] {network.execution_end_time.strftime('%H:%M:%S')}"
            )

        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if value is not None:
                    formatted_key = key.replace("_", " ").title()
                    info_lines.append(f"[bold]{formatted_key}:[/bold] {value}")

        return Panel("\n".join(info_lines), title=f"📊 {title}", border_style="cyan")

    def _create_basic_stats_panel(self, network: "Tasknetwork") -> Panel:
        """
        Create basic network statistics panel.

        :param network: Tasknetwork to extract statistics from
        :return: Rich Panel with network statistics
        """
        stats = self._get_network_statistics(network)

        stats_lines = [
            f"[bold]Total Tasks:[/bold] {stats['total_tasks']}",
            f"[bold]Dependencies:[/bold] {stats['total_dependencies']}",
            f"[green]✅ Completed:[/green] {stats['completed_tasks']}",
            f"[blue]🔵 Running:[/blue] {stats['running_tasks']}",
            f"[yellow]🟡 Ready:[/yellow] {stats['ready_tasks']}",
            f"[red]❌ Failed:[/red] {stats['failed_tasks']}",
        ]

        if stats.get("success_rate") is not None:
            stats_lines.append(
                f"[bold]Success Rate:[/bold] {stats['success_rate']:.1%}"
            )

        return Panel(
            "\n".join(stats_lines), title="📈 Statistics", border_style="green"
        )

    def _add_change_details_to_table(
        self, table: Table, changes: Dict[str, Any]
    ) -> None:
        """
        Add change details to a Rich table.

        :param table: Rich Table instance to add rows to
        :param changes: Dictionary containing detected changes
        """
        if changes.get("added_tasks"):
            count = len(changes["added_tasks"])
            table.add_row("➕ Tasks Added:", f"[green]{count} new tasks[/green]")
            # Show task names if not too many
            if count <= 3:
                task_names = ", ".join(
                    [
                        t[:10] + "..." if len(t) > 10 else t
                        for t in changes["added_tasks"]
                    ]
                )
                table.add_row("", f"[dim]({task_names})[/dim]")

        if changes.get("removed_tasks"):
            count = len(changes["removed_tasks"])
            table.add_row("➖ Tasks Removed:", f"[red]{count} tasks[/red]")
            # Show task names if not too many
            if count <= 3:
                task_names = ", ".join(
                    [
                        t[:10] + "..." if len(t) > 10 else t
                        for t in changes["removed_tasks"]
                    ]
                )
                table.add_row("", f"[dim]({task_names})[/dim]")

        if changes.get("added_dependencies"):
            table.add_row(
                "🔗 Deps Added:",
                f"[green]{len(changes['added_dependencies'])} links[/green]",
            )

        if changes.get("removed_dependencies"):
            table.add_row(
                "🔗 Deps Removed:",
                f"[red]{len(changes['removed_dependencies'])} links[/red]",
            )

        if changes.get("modified_tasks"):
            table.add_row(
                "📝 Tasks Modified:",
                f"[yellow]{len(changes['modified_tasks'])} tasks updated[/yellow]",
            )

    def _add_network_stats_to_table(
        self, table: Table, network: "Tasknetwork"
    ) -> None:
        """
        Add network statistics to the details table.

        :param table: Rich Table instance to add rows to
        :param network: Tasknetwork instance for statistics
        """
        stats = self._get_network_statistics(network)

        table.add_row(
            "📊 Total Tasks:", f"[bold white]{stats['total_tasks']}[/bold white]"
        )
        table.add_row(
            "🔗 Total Deps:", f"[bold white]{stats['total_dependencies']}[/bold white]"
        )

        # Task status breakdown
        status_summary = []
        if stats["completed_tasks"] > 0:
            status_summary.append(f"[green]✅ {stats['completed_tasks']}[/green]")
        if stats["running_tasks"] > 0:
            status_summary.append(f"[blue]🔵 {stats['running_tasks']}[/blue]")
        if stats["ready_tasks"] > 0:
            status_summary.append(f"[yellow]🟡 {stats['ready_tasks']}[/yellow]")
        if stats["failed_tasks"] > 0:
            status_summary.append(f"[red]❌ {stats['failed_tasks']}[/red]")

        if status_summary:
            table.add_row("📈 Task Status:", " | ".join(status_summary))

    def _get_network_statistics(
        self, network: "Tasknetwork"
    ) -> Dict[str, Any]:
        """
        Extract and normalize network statistics.

        :param network: Tasknetwork to extract statistics from
        :return: Normalized statistics dictionary
        """
        # Try to get statistics from network
        if hasattr(network, "get_statistics"):
            stats = network.get_statistics()

            # Handle different statistics formats
            if "task_status_counts" in stats:
                # Format from real Tasknetwork
                status_counts = stats["task_status_counts"]
                return {
                    "total_tasks": stats["total_tasks"],
                    "total_dependencies": stats["total_dependencies"],
                    "completed_tasks": status_counts.get("completed", 0),
                    "failed_tasks": status_counts.get("failed", 0),
                    "running_tasks": status_counts.get("running", 0),
                    "ready_tasks": self._get_ready_task_count(network),
                    "success_rate": self._calculate_success_rate(status_counts),
                }
            else:
                # Format from simple test network
                return {
                    "total_tasks": stats.get("total_tasks", 0),
                    "total_dependencies": stats.get("total_dependencies", 0),
                    "completed_tasks": stats.get("completed_tasks", 0),
                    "failed_tasks": stats.get("failed_tasks", 0),
                    "running_tasks": stats.get("running_tasks", 0),
                    "ready_tasks": stats.get("ready_tasks", 0),
                    "success_rate": stats.get("success_rate"),
                }
        else:
            # Fallback: calculate from network directly
            return self._calculate_basic_statistics(network)

    def _get_ready_task_count(self, network: "Tasknetwork") -> int:
        """
        Get count of ready tasks.

        :param network: Tasknetwork to check
        :return: Number of ready tasks
        """
        try:
            return len(network.get_ready_tasks())
        except AttributeError:
            return 0

    def _calculate_success_rate(self, status_counts: Dict[str, int]) -> Optional[float]:
        """
        Calculate success rate from status counts.

        :param status_counts: Dictionary of task status counts
        :return: Success rate as float or None if no terminal tasks
        """
        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        total_terminal = completed + failed

        return completed / total_terminal if total_terminal > 0 else None

    def _calculate_basic_statistics(
        self, network: "Tasknetwork"
    ) -> Dict[str, Any]:
        """
        Calculate basic statistics directly from network.

        :param network: Tasknetwork to analyze
        :return: Basic statistics dictionary
        """
        # This is a fallback method for networks without get_statistics
        tasks = getattr(network, "tasks", {})
        dependencies = getattr(network, "dependencies", {})

        return {
            "total_tasks": len(tasks),
            "total_dependencies": len(dependencies),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "running_tasks": 0,
            "ready_tasks": 0,
            "success_rate": None,
        }

    def _get_state_text(self, state: networkState) -> str:
        """
        Get formatted network state text.

        :param state: networkState to format
        :return: Formatted state text with color
        """
        state_colors = {
            networkState.CREATED: "yellow",
            networkState.READY: "blue",
            networkState.EXECUTING: "blue",
            networkState.COMPLETED: "green",
            networkState.FAILED: "red",
            networkState.PARTIALLY_FAILED: "orange1",
        }
        color = state_colors.get(state, "white")
        return f"[{color}]{state.value.upper()}[/]"
