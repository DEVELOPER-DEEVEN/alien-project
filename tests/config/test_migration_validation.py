"""
 [Text Cleaned] 
 [Text Cleaned] ， [Text Cleaned] 
"""

import os
import sys
from typing import Any, Dict, List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

sys.path.insert(0, os.path.abspath("."))

from Alien.config import Config as LegacyConfig
from config.config_loader import get_Alien_config

console = Console()


class ConfigValidator:
    """ [Text Cleaned] ： [Text Cleaned] """

    def __init__(self):
        self.mismatches = []
        self.matches = []
        self.legacy_only = []
        self.new_only = []

    def load_configs(self):
        """ [Text Cleaned] """
        console.print("[yellow] [Text Cleaned] ...[/yellow]")

        try:
            legacy_instance = LegacyConfig.get_instance()
            self.legacy_config = legacy_instance.config_data
            console.print("✓  [Text Cleaned] ", style="green")
        except Exception as e:
            console.print(f"✗  [Text Cleaned] : {e}", style="red")
            raise

        try:
            self.new_config = get_Alien_config()
            console.print("✓  [Text Cleaned] ", style="green")
        except Exception as e:
            console.print(f"✗  [Text Cleaned] : {e}", style="red")
            raise

    def get_nested_value(self, config, path: str):
        """ [Text Cleaned] """
        try:
            keys = path.split(".")
            value = config
            for key in keys:
                if isinstance(value, dict):
                    value = value[key]
                else:
                    value = getattr(value, key)
            return value
        except (KeyError, AttributeError):
            return None

    def compare_value(self, path: str, legacy_val, new_val) -> bool:
        """ [Text Cleaned] """
        if legacy_val is None and new_val is None:
            return True
        if legacy_val is None or new_val is None:
            return False

        if hasattr(new_val, "_data"):
            if isinstance(legacy_val, dict):
                return self.compare_value(path, legacy_val, new_val._data)

        if (
            path.endswith("API_BASE")
            and isinstance(legacy_val, str)
            and isinstance(new_val, str)
        ):
            if "chat/completions" in new_val and "chat/completions" not in legacy_val:
                return new_val.startswith(legacy_val.rstrip("/"))

        if isinstance(legacy_val, list) and isinstance(new_val, list):
            if len(legacy_val) != len(new_val):
                return False
            return all(a == b for a, b in zip(legacy_val, new_val))

        if isinstance(legacy_val, dict) and isinstance(new_val, dict):
            if set(legacy_val.keys()) != set(new_val.keys()):
                return False
            return all(
                self.compare_value(f"{path}.{k}", legacy_val[k], new_val.get(k))
                for k in legacy_val.keys()
            )

        return legacy_val == new_val

    def validate_flat_configs(self):
        """ [Text Cleaned] """
        console.print("\n[cyan] [Text Cleaned] ...[/cyan]")

        flat_configs = [
            "MAX_TOKENS",
            "MAX_RETRY",
            "TEMPERATURE",
            "TOP_P",
            "TIMEOUT",
            "MAX_STEP",
            "MAX_ROUND",
            "SLEEP_TIME",
            "RECTANGLE_TIME",
            "ACTION_SEQUENCE",
            "SHOW_VISUAL_OUTLINE_ON_SCREEN",
            "MAXIMIZE_WINDOW",
            "JSON_PARSING_RETRY",
            "SAFE_GUARD",
            "CONTROL_LIST",
            "HISTORY_KEYS",
            "ANNOTATION_COLORS",
            "HIGHLIGHT_BBOX",
            "ANNOTATION_FONT_SIZE",
            "PRINT_LOG",
            "CONCAT_SCREENSHOT",
            "LOG_LEVEL",
            "INCLUDE_LAST_SCREENSHOT",
            "REQUEST_TIMEOUT",
            "LOG_XML",
            "LOG_TO_MARKDOWN",
            "SCREENSHOT_TO_MEMORY",
            "ASK_QUESTION",
            "USE_CUSTOMIZATION",
            "QA_PAIR_FILE",
            "QA_PAIR_NUM",
            "EVA_SESSION",
            "EVA_ROUND",
            "EVA_ALL_SCREENSHOTS",
            "DEFAULT_PNG_COMPRESS_LEVEL",
            "SAVE_UI_TREE",
            "SAVE_FULL_SCREEN",
            "TASK_STATUS",
            "SAVE_EXPERIENCE",
            "USE_MCP",
            "MCP_FALLBACK_TO_UI",
            "MCP_TOOL_TIMEOUT",
            "MCP_LOG_EXECUTION",
            "CLICK_API",
            "AFTER_CLICK_WAIT",
            "INPUT_TEXT_API",
            "INPUT_TEXT_ENTER",
            "INPUT_TEXT_INTER_KEY_PAUSE",
            "USE_APIS",
            "API_PROMPT",
            "CONTROL_BACKEND",
            "IOU_THRESHOLD_FOR_MERGE",
            "HOSTAGENT_PROMPT",
            "APPAGENT_PROMPT",
            "FOLLOWERAGENT_PROMPT",
            "EVALUATION_PROMPT",
        ]

        for config_key in flat_configs:
            legacy_val = self.legacy_config.get(config_key)

            new_val = None
            if hasattr(self.new_config, config_key):
                new_val = getattr(self.new_config, config_key)
            elif hasattr(self.new_config, "system") and hasattr(
                self.new_config.system, config_key.lower()
            ):
                new_val = getattr(self.new_config.system, config_key.lower())

            if legacy_val is not None:
                if self.compare_value(config_key, legacy_val, new_val):
                    self.matches.append((config_key, legacy_val, new_val))
                else:
                    self.mismatches.append((config_key, legacy_val, new_val))

    def validate_agent_configs(self):
        """ [Text Cleaned]  Agent  [Text Cleaned] """
        console.print("\n[cyan] [Text Cleaned]  Agent  [Text Cleaned] ...[/cyan]")

        agents = [
            "HOST_AGENT",
            "APP_AGENT",
            "BACKUP_AGENT",
            "EVALUATION_AGENT",
            "OPERATOR",
        ]
        agent_fields = [
            "VISUAL_MODE",
            "REASONING_MODEL",
            "API_TYPE",
            "API_BASE",
            "API_KEY",
            "API_VERSION",
            "API_MODEL",
            "API_DEPLOYMENT_ID",
            "AAD_TENANT_ID",
            "AAD_API_SCOPE",
            "AAD_API_SCOPE_BASE",
        ]

        for agent in agents:
            if agent not in self.legacy_config:
                continue

            for field in agent_fields:
                legacy_val = self.legacy_config[agent].get(field)
                if legacy_val is None:
                    continue

                new_val = None
                agent_lower = agent.lower()

                if hasattr(self.new_config, agent):
                    agent_obj = getattr(self.new_config, agent)
                    if hasattr(agent_obj, field):
                        new_val = getattr(agent_obj, field)
                    elif hasattr(agent_obj, field.lower()):
                        new_val = getattr(agent_obj, field.lower())

                if new_val is None and hasattr(self.new_config, agent_lower):
                    agent_obj = getattr(self.new_config, agent_lower)
                    if hasattr(agent_obj, field.lower()):
                        new_val = getattr(agent_obj, field.lower())

                if new_val is None:
                    try:
                        new_val = self.new_config[agent][field]
                    except (KeyError, TypeError):
                        pass

                full_path = f"{agent}.{field}"
                if self.compare_value(full_path, legacy_val, new_val):
                    self.matches.append((full_path, legacy_val, new_val))
                else:
                    self.mismatches.append((full_path, legacy_val, new_val))

    def validate_rag_configs(self):
        """ [Text Cleaned]  RAG  [Text Cleaned] """
        console.print("\n[cyan] [Text Cleaned]  RAG  [Text Cleaned] ...[/cyan]")

        rag_configs = [
            "RAG_OFFLINE_DOCS",
            "RAG_OFFLINE_DOCS_RETRIEVED_TOPK",
            "BING_API_KEY",
            "RAG_ONLINE_SEARCH",
            "RAG_ONLINE_SEARCH_TOPK",
            "RAG_ONLINE_RETRIEVED_TOPK",
            "RAG_EXPERIENCE",
            "RAG_EXPERIENCE_RETRIEVED_TOPK",
            "EXPERIENCE_SAVED_PATH",
            "EXPERIENCE_PROMPT",
            "RAG_DEMONSTRATION",
            "RAG_DEMONSTRATION_RETRIEVED_TOPK",
            "RAG_DEMONSTRATION_COMPLETION_N",
            "DEMONSTRATION_SAVED_PATH",
            "DEMONSTRATION_PROMPT",
        ]

        for config_key in rag_configs:
            legacy_val = self.legacy_config.get(config_key)
            if legacy_val is None:
                continue

            new_val = None
            if hasattr(self.new_config, "rag"):
                field_name = config_key.lower().replace("rag_", "")
                if hasattr(self.new_config.rag, field_name):
                    new_val = getattr(self.new_config.rag, field_name)

            if new_val is None and hasattr(self.new_config, config_key):
                new_val = getattr(self.new_config, config_key)

            if self.compare_value(config_key, legacy_val, new_val):
                self.matches.append((config_key, legacy_val, new_val))
            else:
                self.mismatches.append((config_key, legacy_val, new_val))

    def validate_omniparser_config(self):
        """ [Text Cleaned]  Omniparser  [Text Cleaned] """
        console.print("\n[cyan] [Text Cleaned]  Omniparser  [Text Cleaned] ...[/cyan]")

        if "OMNIPARSER" in self.legacy_config:
            legacy_omni = self.legacy_config["OMNIPARSER"]

            for field in [
                "ENDPOINT",
                "BOX_THRESHOLD",
                "IOU_THRESHOLD",
                "USE_PADDLEOCR",
                "IMGSZ",
            ]:
                legacy_val = legacy_omni.get(field)
                if legacy_val is None:
                    continue

                new_val = None
                if hasattr(self.new_config, "OMNIPARSER"):
                    omni = self.new_config.OMNIPARSER
                    if hasattr(omni, field):
                        new_val = getattr(omni, field)
                    elif hasattr(omni, field.lower()):
                        new_val = getattr(omni, field.lower())

                if new_val is None and hasattr(self.new_config, "system"):
                    if hasattr(self.new_config.system, "OMNIPARSER"):
                        omni = self.new_config.system.OMNIPARSER
                        if hasattr(omni, field):
                            new_val = getattr(omni, field)
                        elif hasattr(omni, field.lower()):
                            new_val = getattr(omni, field.lower())
                    elif hasattr(self.new_config.system, "omniparser"):
                        omni = self.new_config.system.omniparser
                        if hasattr(omni, field.lower()):
                            new_val = getattr(omni, field.lower())

                full_path = f"OMNIPARSER.{field}"
                if self.compare_value(full_path, legacy_val, new_val):
                    self.matches.append((full_path, legacy_val, new_val))
                else:
                    self.mismatches.append((full_path, legacy_val, new_val))

    def validate_third_party_configs(self):
        """ [Text Cleaned]  Agent  [Text Cleaned] """
        console.print("\n[cyan] [Text Cleaned]  Agent  [Text Cleaned] ...[/cyan]")

        if "ENABLED_THIRD_PARTY_AGENTS" in self.legacy_config:
            legacy_val = self.legacy_config["ENABLED_THIRD_PARTY_AGENTS"]
            new_val = None

            if hasattr(self.new_config, "ENABLED_THIRD_PARTY_AGENTS"):
                new_val = self.new_config.ENABLED_THIRD_PARTY_AGENTS
            elif hasattr(self.new_config, "third_party"):
                if hasattr(self.new_config.third_party, "ENABLED_THIRD_PARTY_AGENTS"):
                    new_val = self.new_config.third_party.ENABLED_THIRD_PARTY_AGENTS
                elif hasattr(self.new_config.third_party, "enabled_third_party_agents"):
                    new_val = self.new_config.third_party.enabled_third_party_agents
            elif hasattr(self.new_config, "system"):
                if hasattr(self.new_config.system, "ENABLED_THIRD_PARTY_AGENTS"):
                    new_val = self.new_config.system.ENABLED_THIRD_PARTY_AGENTS
                elif hasattr(self.new_config.system, "enabled_third_party_agents"):
                    new_val = self.new_config.system.enabled_third_party_agents

            if self.compare_value("ENABLED_THIRD_PARTY_AGENTS", legacy_val, new_val):
                self.matches.append(("ENABLED_THIRD_PARTY_AGENTS", legacy_val, new_val))
            else:
                self.mismatches.append(
                    ("ENABLED_THIRD_PARTY_AGENTS", legacy_val, new_val)
                )

    def generate_report(self):
        """ [Text Cleaned] """
        console.print("\n" + "=" * 80)
        console.print(
            Panel.fit("[bold green] [Text Cleaned] [/bold green]", border_style="green")
        )

        total = len(self.matches) + len(self.mismatches)
        match_rate = (len(self.matches) / total * 100) if total > 0 else 0

        stats_table = Table(title=" [Text Cleaned] ", box=box.ROUNDED)
        stats_table.add_column(" [Text Cleaned] ", style="cyan")
        stats_table.add_column(" [Text Cleaned] ", style="yellow")
        stats_table.add_column(" [Text Cleaned] ", style="green")

        stats_table.add_row(" [Text Cleaned] ", str(len(self.matches)), f"{match_rate:.2f}%")
        stats_table.add_row(
            " [Text Cleaned] ", str(len(self.mismatches)), f"{100-match_rate:.2f}%"
        )
        stats_table.add_row(" [Text Cleaned] ", str(total), "100%")

        console.print(stats_table)

        if self.mismatches:
            console.print("\n[red]⚠️   [Text Cleaned] ：[/red]")

            mismatch_table = Table(title=" [Text Cleaned] ", box=box.ROUNDED)
            mismatch_table.add_column(" [Text Cleaned] ", style="cyan", no_wrap=True)
            mismatch_table.add_column(" [Text Cleaned] ", style="yellow")
            mismatch_table.add_column(" [Text Cleaned] ", style="magenta")

            for path, legacy_val, new_val in self.mismatches[:20]:                legacy_str = str(legacy_val)[:50] if legacy_val is not None else "None"
                new_str = str(new_val)[:50] if new_val is not None else "None"
                mismatch_table.add_row(path, legacy_str, new_str)

            console.print(mismatch_table)

            if len(self.mismatches) > 20:
                console.print(f"\n...  [Text Cleaned]  {len(self.mismatches) - 20}  [Text Cleaned] ")
        else:
            console.print("\n[bold green]✅  [Text Cleaned] ！[/bold green]")

        console.print("\n" + "=" * 80)
        if match_rate >= 95:
            console.print("[bold green]✅  [Text Cleaned] ！ [Text Cleaned]  >= 95%[/bold green]")
            return True
        else:
            console.print(
                f"[bold red]❌  [Text Cleaned] ！ [Text Cleaned] : {match_rate:.2f}% < 95%[/bold red]"
            )
            return False

    def run(self):
        """ [Text Cleaned] """
        try:
            self.load_configs()
            self.validate_flat_configs()
            self.validate_agent_configs()
            self.validate_rag_configs()
            self.validate_omniparser_config()
            self.validate_third_party_configs()

            success = self.generate_report()
            return success
        except Exception as e:
            console.print(f"\n[bold red] [Text Cleaned] : {e}[/bold red]")
            import traceback

            console.print(traceback.format_exc())
            return False


if __name__ == "__main__":
    console.print(
        Panel.fit(
            "[bold cyan]Alien³  [Text Cleaned] [/bold cyan]\n"
            " [Text Cleaned] ， [Text Cleaned] ",
            border_style="cyan",
        )
    )

    validator = ConfigValidator()
    success = validator.run()

    sys.exit(0 if success else 1)
