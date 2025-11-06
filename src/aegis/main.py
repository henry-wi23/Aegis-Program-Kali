from aegis.core.orchestrator import Orchestrator
from aegis.utils.logger import setup_logger


def main() -> None:
    """
    The main entry point for the Aegis Program.
    Initializes and runs the main Orchestrator.
    """
    logger = setup_logger('aegis_main', module_code='MAIN', script_code='EXEC')

    logger.info("Aegis Program Initializing...")

    orchestrator = Orchestrator()

    research_task = (
        "Research the concept of Byzantine Fault Tolerance and synthesize its key principles "
        "for resilient distributed systems."
    )
    delegation_result = orchestrator.execute_task(research_task)

    print("\n\n===== CUSTOM AGENT FRAMEWORK RESULT =====\n")
    print(delegation_result)
    print("\n==========================================\n")

    logger.info("Custom agent framework workflow executed.")

    logger.info("Aegis Program shutting down.")


if __name__ == "__main__":
    main()
