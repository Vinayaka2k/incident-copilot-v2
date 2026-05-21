from agent import IncidentAgent


class InvestigationService:

    @staticmethod
    def run_investigation(incident: dict):
        """
        Runs the AI investigation workflow
        for a given incident.
        """

        # mark incident as running
        incident["status"] = "RUNNING"

        # initialize agent
        agent = IncidentAgent(incident)

        # execute investigation pipeline
        result = agent.run()

        return result