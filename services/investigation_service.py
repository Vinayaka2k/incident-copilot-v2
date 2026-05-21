from agent import IncidentAgent


class InvestigationService:
    """
    Thin wrapper around IncidentAgent.

    NOTE:
    In MVP, this is optional and can be skipped.
    main.py can directly call IncidentAgent.
    """

    @staticmethod
    def run_investigation(incident: dict):
        agent = IncidentAgent(incident)
        return agent.run()