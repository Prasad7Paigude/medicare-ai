"""aiXplain AI Doctor integration for MediCare.

Manages the lifecycle of the aiXplain conversational agent, including
session tracking per user and message dispatch.
"""

import logging

from aixplain.factories.agent_factory import AgentFactory
from aixplain.modules.agent.tool.model_tool import ModelTool
from aixplain.modules.agent.tool.pipeline_tool import PipelineTool
from aixplain.enums import Function, Supplier

from config.settings import TEAM_API_KEY, AIXPLAIN_AGENT_ID, AIXPLAIN_PIPELINE_ID

logger = logging.getLogger(__name__)


class AIDoctorAgent:
    """Wrapper around the aiXplain conversational agent for MediCare.

    Attributes:
        agent: The underlying aiXplain ``Agent`` instance, or ``None``
            if initialisation failed.
        user_sessions: Mapping of user identifier to active session id.
    """

    def __init__(self) -> None:
        self.agent = None
        self.user_sessions: dict = {}
        self._initialise()

    def _initialise(self) -> None:
        """Create or retrieve the aiXplain agent and its tools."""
        try:
            speech_tool = ModelTool(
                function=Function.SPEECH_SYNTHESIS,
                supplier=Supplier.GOOGLE,
            )
            ner_tool = ModelTool(
                function=Function.NAMED_ENTITY_RECOGNITION,
                supplier=Supplier.MICROSOFT,
            )
            pipeline_tool = PipelineTool(
                description="MediCare",
                pipeline=AIXPLAIN_PIPELINE_ID,
            )

            self.agent = AgentFactory.get(AIXPLAIN_AGENT_ID)
            logger.info(
                "aiXplain agent initialised (id=%s, tools=%d)",
                self.agent.id,
                len([speech_tool, ner_tool, pipeline_tool]),
            )
        except Exception as exc:
            logger.error("Failed to initialise aiXplain agent: %s", exc, exc_info=True)
            self.agent = None

    def process_message(self, user_input: str, user_id: str) -> dict:
        """Send a user message to the AI Doctor and return the response.

        Args:
            user_input: The message text from the user.
            user_id: Unique identifier for the user (used to track sessions).

        Returns:
            A dict with keys ``success`` (bool) and ``message`` (str).
            On failure, ``success`` is ``False``.
        """
        if self.agent is None:
            logger.warning("AI Doctor request blocked: agent unavailable (user=%s)", user_id)
            return {
                "success": False,
                "message": "AI Doctor service is currently unavailable. Please try again later.",
            }

        try:
            session_id = self.user_sessions.get(user_id)

            if session_id:
                logger.debug("Continuing session %s for user %s", session_id, user_id)
                response = self.agent.run(user_input, session_id=session_id)
            else:
                logger.debug("Starting new conversation for user %s", user_id)
                response = self.agent.run(user_input)

                if (
                    isinstance(response, dict)
                    and "data" in response
                    and "session_id" in response["data"]
                ):
                    new_sid = response["data"]["session_id"]
                    self.user_sessions[user_id] = new_sid
                    logger.info("Created session %s for user %s", new_sid, user_id)

            output_text: str = "I'm sorry, I couldn't process your request properly. Please try again."
            if isinstance(response, dict) and "data" in response:
                output_text = response["data"].get("output", output_text)
            else:
                logger.warning("Unexpected agent response format: %s", response)

            logger.info("AI Doctor | user=%s | input=%.80s", user_id, user_input)
            return {"success": True, "message": output_text}

        except Exception as exc:
            logger.error(
                "AI Doctor error (user=%s): %s", user_id, exc, exc_info=True
            )
            return {
                "success": False,
                "message": "I'm sorry, I encountered an error while processing your request. Please try again later.",
            }
