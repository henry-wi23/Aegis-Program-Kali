from typing import Any, Dict, List, Optional

import yaml

from aegis.agents.base import AegisAgent, AegisTool
from aegis.utils.logger import setup_logger


class AgentManager:
    """Manage agent configuration and provide agent instances on request."""

    def __init__(self, config_path: str = "config/agents.yaml") -> None:
        self.logger = setup_logger('AgentManager', module_code='AGNT', script_code='MGR')
        self.logger.info("Loading agent configurations from '%s'...", config_path)
        self.agent_configs: Dict[str, Dict[str, Any]] = {}

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file) or {}

            if not isinstance(data, dict):
                self.logger.error(
                    "Agent configuration file '%s' must contain a mapping.",
                    config_path,
                    extra={'error_code': 'CONF-TYPE'}
                )
                return

            # ensure nested structures are dictionaries to avoid mutation surprises
            self.agent_configs = {
                str(name): dict(config) if isinstance(config, dict) else {}
                for name, config in data.items()
            }
            self.logger.info("Agent configurations loaded successfully.")

        except FileNotFoundError:
            self.logger.error(
                "Agent configuration file not found at '%s'.",
                config_path,
                extra={'error_code': 'CONF-404'}
            )
        except yaml.YAMLError as exc:
            self.logger.error(
                "Error parsing YAML in '%s': %s",
                config_path,
                exc,
                extra={'error_code': 'CONF-YAML-ERR'}
            )

    def get_agent(self, agent_name: str) -> Optional[AegisAgent]:
        """Return a fully instantiated agent for the requested name, if available."""

        config = self.agent_configs.get(agent_name)
        if not config:
            self.logger.warning("Agent '%s' not found in configuration.", agent_name)
            return None

        agent = self._build_agent(agent_name, config)
        if agent is None:
            self.logger.error(
                "Failed to instantiate '%s' agent due to missing or invalid configuration.",
                agent_name,
                extra={'error_code': 'CONF-AGENT-INIT'}
            )
        else:
            self.logger.info("Instantiated '%s' agent with role '%s'.", agent_name, agent.role)

        return agent

    def _build_agent(self, agent_name: str, config: Dict[str, Any]) -> Optional[AegisAgent]:
        """Construct an AegisAgent from raw configuration data."""

        role = self._extract_str_field(agent_name, config, 'role')
        goal = self._extract_str_field(agent_name, config, 'goal')
        backstory = self._extract_str_field(agent_name, config, 'backstory')

        if not all([role, goal, backstory]):
            return None

        tools = self._build_tools(agent_name, config.get('tools', []))

        return AegisAgent(role=role, goal=goal, backstory=backstory, tools=tools)

    def _build_tools(self, agent_name: str, tools_data: Any) -> List[AegisTool]:
        """Build a list of tools from configuration, ignoring malformed entries."""

        tools: List[AegisTool] = []

        if not tools_data:
            return tools

        if not isinstance(tools_data, list):
            self.logger.warning(
                "Tools configuration for agent '%s' must be a list; received %s.",
                agent_name,
                type(tools_data).__name__
            )
            return tools

        for tool_entry in tools_data:
            if not isinstance(tool_entry, dict):
                self.logger.warning(
                    "Skipping malformed tool entry for agent '%s': %s",
                    agent_name,
                    tool_entry
                )
                continue

            name = tool_entry.get('name')
            description = tool_entry.get('description')
            func = tool_entry.get('func')

            if not all([name, description, callable(func)]):
                self.logger.warning(
                    "Tool entry missing required fields for agent '%s': %s",
                    agent_name,
                    tool_entry
                )
                continue

            tools.append(AegisTool(name=str(name), description=str(description), func=func))

        return tools

    def _extract_str_field(self, agent_name: str, config: Dict[str, Any], field_name: str) -> str:
        """Pull a string field from the configuration while providing logging."""

        value = config.get(field_name)
        if value is None:
            self.logger.error(
                "Agent '%s' configuration missing required field '%s'.",
                agent_name,
                field_name,
                extra={'error_code': 'CONF-MISSING-FIELD'}
            )
            return ''

        if not isinstance(value, str):
            self.logger.warning(
                "Field '%s' for agent '%s' expected to be a string; received %s.",
                field_name,
                agent_name,
                type(value).__name__
            )
            return str(value)

        return value.strip()
