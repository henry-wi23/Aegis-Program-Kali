from typing import Any, Callable, List

from pydantic import BaseModel, ConfigDict, Field

from aegis.utils.logger import setup_logger

_logger = setup_logger('AgentBase', module_code='AGNT', script_code='BASE')


def _default_tools() -> List['AegisTool']:
    """Return a fresh tool list for agent initialization."""

    return []


class AegisTool(BaseModel):
    """A data contract for a tool that an agent can use."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    func: Callable[..., Any]


class AegisAgent(BaseModel):
    """A data contract representing a specialized agent in the Aegis system."""

    role: str
    goal: str
    backstory: str
    tools: List[AegisTool] = Field(default_factory=_default_tools)


class AegisTask(BaseModel):
    """A data contract representing a single task to be executed by an agent."""

    description: str
    expected_output: str
    agent: AegisAgent

    def log_creation(self) -> None:
        _logger.info("Created task for agent '%s' with goal '%s'.", self.agent.role, self.agent.goal)
