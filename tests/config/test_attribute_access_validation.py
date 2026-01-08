"""
 [Text Cleaned] 
 [Text Cleaned] ， [Text Cleaned] 
"""

import os
import sys
from typing import Any
from rich.console import Console
from rich.table import Table
from rich import box

sys.path.insert(0, os.path.abspath("."))

from Alien.config import Config as LegacyConfig
from config.config_loader import get_Alien_config, get_cluster_config

console = Console()


class AttributeAccessValidator:
    """ [Text Cleaned] """

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def test_value(
        self, name: str, legacy_val: Any, new_val_upper: Any, new_val_lower: Any = None
    ):
        """
         [Text Cleaned] 

        :param name:  [Text Cleaned] 
        :param legacy_val:  [Text Cleaned] 
        :param new_val_upper:  [Text Cleaned] 
        :param new_val_lower:  [Text Cleaned] （ [Text Cleaned] ）
        """
        result = {
            "name": name,
            "legacy": legacy_val,
            "new_upper": new_val_upper,
            "new_lower": new_val_lower,
            "status": "✓",
        }

        if hasattr(new_val_upper, "_data"):
            new_val_upper = new_val_upper._data
        if new_val_lower is not None and hasattr(new_val_lower, "_data"):
            new_val_lower = new_val_lower._data

        if self._compare_values(legacy_val, new_val_upper):
            if new_val_lower is not None:
                if not self._compare_values(new_val_upper, new_val_lower):
                    result["status"] = "✗"
                    result["error"] = " [Text Cleaned] "
                    self.failed += 1
                else:
                    self.passed += 1
            else:
                self.passed += 1
        else:
            result["status"] = "✗"
            result["error"] = " [Text Cleaned] "
            self.failed += 1

        self.test_results.append(result)
        return result["status"] == "✓"

    def _compare_values(self, val1: Any, val2: Any) -> bool:
        """ [Text Cleaned] """
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False

        if isinstance(val1, str) and isinstance(val2, str):
            if "chat/completions" in val2 and "chat/completions" not in val1:
                return val2.startswith(val1.rstrip("/"))

        if isinstance(val1, list) and isinstance(val2, list):
            if len(val1) != len(val2):
                return False
            return all(a == b for a, b in zip(val1, val2))

        if isinstance(val1, dict) and isinstance(val2, dict):
            if set(val1.keys()) != set(val2.keys()):
                return False
            return all(self._compare_values(val1[k], val2.get(k)) for k in val1.keys())

        return val1 == val2

    def test_Alien_system_config(self):
        """ [Text Cleaned]  Alien SystemConfig  [Text Cleaned] """
        console.print("\n[bold cyan] [Text Cleaned]  Alien SystemConfig  [Text Cleaned] [/bold cyan]")

        legacy = LegacyConfig.get_instance().config_data
        new_config = get_Alien_config()

        system_fields = [
            ("MAX_TOKENS", "max_tokens"),
            ("MAX_RETRY", "max_retry"),
            ("MAX_STEP", "max_step"),
            ("MAX_ROUND", "max_round"),
            ("TEMPERATURE", "temperature"),
            ("TIMEOUT", "timeout"),
            ("LOG_LEVEL", "log_level"),
            ("PRINT_LOG", "print_log"),
        ]

        for upper_name, lower_name in system_fields:
            if upper_name in legacy:
                legacy_val = legacy[upper_name]
                new_val_upper = getattr(new_config.system, upper_name, None)
                new_val_lower = getattr(new_config.system, lower_name, None)

                self.test_value(
                    f"system.{upper_name}", legacy_val, new_val_upper, new_val_lower
                )

    def test_Alien_agent_config(self):
        """ [Text Cleaned]  Alien AgentConfig  [Text Cleaned] """
        console.print("\n[bold cyan] [Text Cleaned]  Alien AgentConfig  [Text Cleaned] [/bold cyan]")

        legacy = LegacyConfig.get_instance().config_data
        new_config = get_Alien_config()

        agents = [
            ("HOST_AGENT", "host_agent"),
            ("APP_AGENT", "app_agent"),
        ]

        agent_fields = [
            ("VISUAL_MODE", "visual_mode"),
            ("REASONING_MODEL", "reasoning_model"),
            ("API_TYPE", "api_type"),
            ("API_BASE", "api_base"),
            ("API_KEY", "api_key"),
            ("API_VERSION", "api_version"),
            ("API_MODEL", "api_model"),
        ]

        for agent_upper, agent_lower in agents:
            if agent_upper not in legacy:
                continue

            legacy_agent = legacy[agent_upper]
            new_agent = getattr(new_config, agent_lower)

            for field_upper, field_lower in agent_fields:
                if field_upper in legacy_agent:
                    legacy_val = legacy_agent[field_upper]
                    new_val_upper = getattr(new_agent, field_upper, None)
                    new_val_lower = getattr(new_agent, field_lower, None)

                    self.test_value(
                        f"{agent_lower}.{field_upper}",
                        legacy_val,
                        new_val_upper,
                        new_val_lower,
                    )

    def test_Alien_rag_config(self):
        """ [Text Cleaned]  Alien RAGConfig  [Text Cleaned] """
        console.print("\n[bold cyan] [Text Cleaned]  Alien RAGConfig  [Text Cleaned] [/bold cyan]")

        legacy = LegacyConfig.get_instance().config_data
        new_config = get_Alien_config()

        rag_fields = [
            ("RAG_OFFLINE_DOCS", "offline_docs"),
            ("RAG_OFFLINE_DOCS_RETRIEVED_TOPK", "offline_docs_retrieved_topk"),
            ("RAG_ONLINE_SEARCH", "online_search"),
            ("RAG_ONLINE_SEARCH_TOPK", "online_search_topk"),
            ("RAG_EXPERIENCE", "experience"),
            ("RAG_EXPERIENCE_RETRIEVED_TOPK", "experience_retrieved_topk"),
            ("RAG_DEMONSTRATION", "demonstration"),
            ("RAG_DEMONSTRATION_RETRIEVED_TOPK", "demonstration_retrieved_topk"),
        ]

        for upper_name, lower_name in rag_fields:
            if upper_name in legacy:
                legacy_val = legacy[upper_name]
                new_val_upper = getattr(new_config.rag, upper_name, None)
                new_val_lower = getattr(new_config.rag, lower_name, None)

                self.test_value(
                    f"rag.{upper_name}", legacy_val, new_val_upper, new_val_lower
                )

    def test_cluster_network_config(self):
        """ [Text Cleaned]  cluster networkRuntimeConfig  [Text Cleaned] """
        console.print(
            "\n[bold cyan] [Text Cleaned]  cluster networkRuntimeConfig  [Text Cleaned] [/bold cyan]"
        )

        try:
            cluster_config = get_cluster_config()

            network_fields = [
                ("network_ID", "network_id"),
                ("HEARTBEAT_INTERVAL", "heartbeat_interval"),
                ("RECONNECT_DELAY", "reconnect_delay"),
                ("MAX_CONCURRENT_TASKS", "max_concurrent_tasks"),
                ("MAX_STEP", "max_step"),
                ("DEVICE_INFO", "device_info"),
            ]

            for upper_name, lower_name in network_fields:
                new_val_upper = getattr(cluster_config.network, upper_name, None)
                new_val_lower = getattr(cluster_config.network, lower_name, None)

                result = {
                    "name": f"network.{upper_name}",
                    "new_upper": new_val_upper,
                    "new_lower": new_val_lower,
                    "status": (
                        "✓"
                        if self._compare_values(new_val_upper, new_val_lower)
                        else "✗"
                    ),
                }

                if result["status"] == "✓":
                    self.passed += 1
                else:
                    self.failed += 1
                    result["error"] = " [Text Cleaned] "

                self.test_results.append(result)

        except Exception as e:
            console.print(f"[yellow]cluster  [Text Cleaned] : {e}[/yellow]")

    def test_cluster_agent_config(self):
        """ [Text Cleaned]  cluster AgentConfig  [Text Cleaned] """
        console.print(
            "\n[bold cyan] [Text Cleaned]  cluster network_AGENT  [Text Cleaned] [/bold cyan]"
        )

        try:
            cluster_config = get_cluster_config()
            agent = cluster_config.agent.network_AGENT

            agent_fields = [
                ("VISUAL_MODE", "visual_mode"),
                ("REASONING_MODEL", "reasoning_model"),
                ("API_TYPE", "api_type"),
                ("API_BASE", "api_base"),
                ("API_MODEL", "api_model"),
                ("API_VERSION", "api_version"),
            ]

            for upper_name, lower_name in agent_fields:
                new_val_upper = getattr(agent, upper_name, None)
                new_val_lower = getattr(agent, lower_name, None)

                result = {
                    "name": f"network_agent.{upper_name}",
                    "new_upper": new_val_upper,
                    "new_lower": new_val_lower,
                    "status": (
                        "✓"
                        if self._compare_values(new_val_upper, new_val_lower)
                        else "✗"
                    ),
                }

                if result["status"] == "✓":
                    self.passed += 1
                else:
                    self.failed += 1
                    result["error"] = " [Text Cleaned] "

                self.test_results.append(result)

        except Exception as e:
            console.print(f"[yellow]cluster Agent  [Text Cleaned] : {e}[/yellow]")

    def print_summary(self):
        """ [Text Cleaned] """
        console.print("\n" + "=" * 70)
        console.print("[bold] [Text Cleaned] [/bold]")
        console.print("=" * 70)

        table = Table(box=box.ROUNDED)
        table.add_column(" [Text Cleaned] ", style="cyan")
        table.add_column(" [Text Cleaned] ", justify="right", style="yellow")
        table.add_column(" [Text Cleaned] ", justify="right", style="green")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        table.add_row(" [Text Cleaned] ", str(self.passed), f"{pass_rate:.2f}%")
        table.add_row(" [Text Cleaned] ", str(self.failed), f"{(100-pass_rate):.2f}%")
        table.add_row(" [Text Cleaned] ", str(total), "100%")

        console.print(table)

        if self.failed > 0:
            console.print("\n[bold red] [Text Cleaned] :[/bold red]")
            for result in self.test_results:
                if result["status"] == "✗":
                    console.print(
                        f"  ✗ {result['name']}: {result.get('error', ' [Text Cleaned] ')}"
                    )
                    if "legacy" in result:
                        console.print(f"     [Text Cleaned] : {result['legacy']}")
                    console.print(f"     [Text Cleaned] : {result['new_upper']}")
                    console.print(f"     [Text Cleaned] : {result['new_lower']}")

        if self.failed == 0:
            console.print("\n[bold green]✅  [Text Cleaned] ！[/bold green]")
            return True
        else:
            console.print(f"\n[bold red]❌ {self.failed}  [Text Cleaned] [/bold red]")
            return False


def main():
    """ [Text Cleaned] """
    console.print("\n" + "=" * 70)
    console.print("[bold] [Text Cleaned] [/bold]")
    console.print("=" * 70)
    console.print(" [Text Cleaned] / [Text Cleaned] \n")

    validator = AttributeAccessValidator()

    try:
        validator.test_Alien_system_config()
        validator.test_Alien_agent_config()
        validator.test_Alien_rag_config()

        validator.test_cluster_network_config()
        validator.test_cluster_agent_config()

        success = validator.print_summary()

        return 0 if success else 1

    except Exception as e:
        console.print(f"\n[bold red] [Text Cleaned] : {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
