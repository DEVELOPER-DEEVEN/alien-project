
"""
Orion-specific visualization display components.

This module provides specialized display functionality for orion-related
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
    from ..orion.task_orion import TaskOrion

from ..orion.enums import OrionState


class OrionDisplay:
    """
    Specialized display components for orion visualization.

    Provides reusable, modular components for displaying orion information
    with consistent Rich formatting across different contexts.
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize OrionDisplay.

        :param console: Optional Rich Console instance for output
        """
        self.console = console or Console()

    def display_orion_started(
        self,
        orion: "TaskOrion",
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display orion start notification.

        :param orion: TaskOrion that started
        :param additional_info: Optional additional information
        """
        # Create orion info
        info_panel = self._create_basic_info_panel(
            orion, "🚀 Orion Started", additional_info
        )

        # Create basic stats
        stats_panel = self._create_basic_stats_panel(orion)

        # Display side by side
        self.console.print()
        self.console.rule("[bold cyan]🚀 Orion Started[/bold cyan]")
        self.console.print(Columns([info_panel, stats_panel], equal=True))

    def display_orion_completed(
        self,
        orion: "TaskOrion",
        execution_time: Optional[float] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display orion completion notification with enhanced formatting.

        :param orion: TaskOrion that completed
        :param execution_time: Total execution time in seconds
        :param additional_info: Optional additional information
        """
        from .orion_formatter import OrionFormatter

        # Prepare data for the formatter
        stats = (
            orion.get_statistics()
            if hasattr(orion, "get_statistics")
            else {}
        )

        orion_data = {
            "id": orion.orion_id,
            "name": orion.name or orion.orion_id,
            "state": (
                orion.state.value
                if hasattr(orion.state, "value")
                else str(orion.state)
            ),
            "total_tasks": (
                len(orion.tasks) if hasattr(orion, "tasks") else 0
            ),
            "execution_duration": execution_time or 0,
            "statistics": stats,
            "orion": str(orion),
        }

        # Add timing information if available
        if hasattr(orion, "created_at") and orion.created_at:
            orion_data["created"] = orion.created_at.strftime(
                "%H:%M:%S"
            )

        if (
            hasattr(orion, "execution_start_time")
            and orion.execution_start_time
        ):
            orion_data["started"] = orion.execution_start_time.strftime(
                "%H:%M:%S"
            )

        if (
            hasattr(orion, "execution_end_time")
            and orion.execution_end_time
        ):
            orion_data["ended"] = orion.execution_end_time.strftime(
                "%H:%M:%S"
            )

        # Merge additional info
        if additional_info:
            orion_data.update(additional_info)

        # Use the new formatter to display
        formatter = OrionFormatter()
        formatter.display_orion_result(orion_data)

    def display_orion_failed(
        self,
        orion: "TaskOrion",
        error: Optional[Exception] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display orion failure notification.

        :param orion: TaskOrion that failed
        :param error: Exception that caused the failure
        :param additional_info: Optional additional information
        """
        # Enhance additional info with error
        enhanced_info = additional_info.copy() if additional_info else {}
        if error:
            enhanced_info["error"] = str(error)[:100]

        # Create failure info
        info_panel = self._create_basic_info_panel(
            orion, "❌ Orion Failed", enhanced_info
        )

        # Create stats with failure emphasis
        stats_panel = self._create_basic_stats_panel(orion)

        # Display with error styling
        self.console.print()
        self.console.rule("[bold red]❌ Orion Failed[/bold red]")
        self.console.print(Columns([info_panel, stats_panel], equal=True))

    def display_orion_modified(
        self,
        orion: "TaskOrion",
        changes: Dict[str, Any],
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Display orion modification notification with change details.

        :param orion: Modified TaskOrion
        :param changes: Dictionary containing detected changes
        :param additional_info: Optional additional information
        """
        # Create modification message
        mod_text = Text()
        mod_text.append("🔄 ", style="bold blue")
        mod_text.append(f"Orion Modified: ", style="bold blue")
        mod_text.append(f"{orion.name}", style="bold yellow")
        mod_text.append(f" ({orion.orion_id[:8]}...)", style="dim")

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
        self._add_orion_stats_to_table(table, orion)

        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if value is not None:
                    table.add_row(f"ℹ️ {key.title()}:", f"[cyan]{value}[/cyan]")

        # Create panel with proper Rich composition
        content = Group(mod_text, "", table)

        panel = Panel(
            content,
            title="[bold blue]⚙️ Orion Structure Updated[/bold blue]",
            border_style="blue",
            width=80,
        )

        self.console.print(panel)

    def _create_basic_info_panel(
        self,
        orion: "TaskOrion",
        title: str,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Panel:
        """
        Create basic orion information panel.

        :param orion: TaskOrion to display info for
        :param title: Panel title
        :param additional_info: Optional additional information
        :return: Rich Panel with orion information
        """
        info_lines = [
            f"[bold]ID:[/bold] {orion.orion_id[:12]}...",
            f"[bold]Name:[/bold] {orion.name or 'Unnamed'}",
            f"[bold]State:[/bold] {self._get_state_text(orion.state)}",
        ]

        # Add timing information if available
        if hasattr(orion, "created_at") and orion.created_at:
            info_lines.append(
                f"[bold]Created:[/bold] {orion.created_at.strftime('%H:%M:%S')}"
            )

        if (
            hasattr(orion, "execution_start_time")
            and orion.execution_start_time
        ):
            info_lines.append(
                f"[bold]Started:[/bold] {orion.execution_start_time.strftime('%H:%M:%S')}"
            )

        if (
            hasattr(orion, "execution_end_time")
            and orion.execution_end_time
        ):
            info_lines.append(
                f"[bold]Ended:[/bold] {orion.execution_end_time.strftime('%H:%M:%S')}"
            )

        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if value is not None:
                    formatted_key = key.replace("_", " ").title()
                    info_lines.append(f"[bold]{formatted_key}:[/bold] {value}")

        return Panel("\n".join(info_lines), title=f"📊 {title}", border_style="cyan")

    def _create_basic_stats_panel(self, orion: "TaskOrion") -> Panel:
        """
        Create basic orion statistics panel.

        :param orion: TaskOrion to extract statistics from
        :return: Rich Panel with orion statistics
        """
        stats = self._get_orion_statistics(orion)

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

    def _add_orion_stats_to_table(
        self, table: Table, orion: "TaskOrion"
    ) -> None:
        """
        Add orion statistics to the details table.

        :param table: Rich Table instance to add rows to
        :param orion: TaskOrion instance for statistics
        """
        stats = self._get_orion_statistics(orion)

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

    def _get_orion_statistics(
        self, orion: "TaskOrion"
    ) -> Dict[str, Any]:
        """
        Extract and normalize orion statistics.

        :param orion: TaskOrion to extract statistics from
        :return: Normalized statistics dictionary
        """
        # Try to get statistics from orion
        if hasattr(orion, "get_statistics"):
            stats = orion.get_statistics()

            # Handle different statistics formats
            if "task_status_counts" in stats:
                # Format from real TaskOrion
                status_counts = stats["task_status_counts"]
                return {
                    "total_tasks": stats["total_tasks"],
                    "total_dependencies": stats["total_dependencies"],
                    "completed_tasks": status_counts.get("completed", 0),
                    "failed_tasks": status_counts.get("failed", 0),
                    "running_tasks": status_counts.get("running", 0),
                    "ready_tasks": self._get_ready_task_count(orion),
                    "success_rate": self._calculate_success_rate(status_counts),
                }
            else:
                # Format from simple test orion
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
            # Fallback: calculate from orion directly
            return self._calculate_basic_statistics(orion)

    def _get_ready_task_count(self, orion: "TaskOrion") -> int:
        """
        Get count of ready tasks.

        :param orion: TaskOrion to check
        :return: Number of ready tasks
        """
        try:
            return len(orion.get_ready_tasks())
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
        self, orion: "TaskOrion"
    ) -> Dict[str, Any]:
        """
        Calculate basic statistics directly from orion.

        :param orion: TaskOrion to analyze
        :return: Basic statistics dictionary
        """
        # This is a fallback method for orions without get_statistics
        tasks = getattr(orion, "tasks", {})
        dependencies = getattr(orion, "dependencies", {})

        return {
            "total_tasks": len(tasks),
            "total_dependencies": len(dependencies),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "running_tasks": 0,
            "ready_tasks": 0,
            "success_rate": None,
        }

    def _get_state_text(self, state: OrionState) -> str:
        """
        Get formatted orion state text.

        :param state: OrionState to format
        :return: Formatted state text with color
        """
        state_colors = {
            OrionState.CREATED: "yellow",
            OrionState.READY: "blue",
            OrionState.EXECUTING: "blue",
            OrionState.COMPLETED: "green",
            OrionState.FAILED: "red",
            OrionState.PARTIALLY_FAILED: "orange1",
        }
        color = state_colors.get(state, "white")
        return f"[{color}]{state.value.upper()}[/]"
