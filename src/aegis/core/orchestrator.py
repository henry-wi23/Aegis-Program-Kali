from aegis.agents.agent_manager import AgentManager
from aegis.agents.base import AegisTask
from aegis.hardware.manager import HardwareManager
from aegis.utils.logger import setup_logger


class Orchestrator:
	"""Coordinate hardware awareness and agent delegation for Aegis."""

	def __init__(self) -> None:
		self.logger = setup_logger('Orchestrator', module_code='CORE', script_code='ORCH')
		self.logger.info("Orchestrator initializing...")
		self.hardware_manager = HardwareManager()
		self.agent_manager = AgentManager()
		self.logger.info("Orchestrator initialization complete.")

	def execute_task(self, task_description: str) -> str:
		"""Route the task to the appropriate subsystem or agent."""

		self.logger.info("Received task: '%s'", task_description)
		lowered_task = task_description.lower()

		if "hardware status" in lowered_task:
			self.logger.info("Task identified as hardware status query. Accessing HAL.")
			state = self.hardware_manager.get_hardware_state()
			report = state.model_dump_json(indent=2)
			self.logger.info("Successfully generated hardware status report.")
			return report

		if "research" in lowered_task:
			return self._handle_research_task(task_description)

		self.logger.warning("Task not yet implemented: '%s'", task_description)
		return "Task not recognized."

	def _handle_research_task(self, task_description: str) -> str:
		"""Delegate research-centric tasks to the configured research agent."""

		researcher = self.agent_manager.get_agent('research_agent')
		if researcher is None:
			self.logger.error(
				"Delegation failed: Research agent could not be instantiated.",
				extra={'error_code': 'ORCH-NO-AGENT'}
			)
			return "Delegation failed: ResearchAgent not available."

		task = AegisTask(
			description=task_description,
			expected_output="A comprehensive research briefing addressing the request.",
			agent=researcher,
		)
		task.log_creation()

		self.logger.info(
			"Delegated research task to agent role '%s' with goal '%s'.",
			researcher.role,
			researcher.goal,
		)

		return (
			"Task execution initiated via custom agent framework.\n"
			f"Agent Role: {researcher.role}\n"
			f"Agent Goal: {researcher.goal}\n"
			f"Expected Output: {task.expected_output}"
		)

