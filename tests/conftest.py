"""Global test fixtures and mocks for the MediCare test suite.

The ``aixplain`` SDK makes HTTP calls at import time (loading function
definitions from the platform API).  Because tests must not require live
credentials or network access, we mock the relevant ``aixplain`` modules
before any application code is imported.
"""

import os
import sys
from unittest.mock import MagicMock, PropertyMock

# ── Isolate tests from live credentials ───────────────────────────────────
os.environ.setdefault("FLASK_DEBUG", "false")
os.environ["MONGODB_URI"] = ""
os.environ["TEAM_API_KEY"] = "test-dummy-key"
os.environ["AIXPLAIN_AGENT_ID"] = ""
os.environ["AIXPLAIN_PIPELINE_ID"] = ""
os.environ["MAIL_HOST"] = ""
os.environ["MAIL_PORT"] = "0"
os.environ["MAIL_USERNAME"] = ""
os.environ["MAIL_PASSWORD"] = ""
os.environ["MAIL_DEFAULT_SENDER"] = ""

# ── Mock aixplain modules that make HTTP calls at import time ─────────────
_mock_function = MagicMock()
_mock_function.Function = MagicMock()
_mock_function.Supplier = MagicMock()
_mock_function.FunctionInputOutput = MagicMock()

_mock_agent_tool = MagicMock()

_mock_agent_factory = MagicMock()
_mock_agent_factory.AgentFactory = MagicMock()

# Build minimal mocks for the classes used by src/ai_doctor.py
fake_model_tool = MagicMock()
fake_pipeline_tool = MagicMock()

_modules = {
    "aixplain": MagicMock(),
    "aixplain.enums": _mock_function,
    "aixplain.enums.Function": PropertyMock(),
    "aixplain.enums.Supplier": PropertyMock(),
    "aixplain.factories": MagicMock(),
    "aixplain.factories.agent_factory": _mock_agent_factory,
    "aixplain.factories.agent_factory.AgentFactory": MagicMock(),
    "aixplain.modules": MagicMock(),
    "aixplain.modules.agent": MagicMock(),
    "aixplain.modules.agent.tool": _mock_agent_tool,
    "aixplain.modules.agent.tool.model_tool": MagicMock(),
    "aixplain.modules.agent.tool.model_tool.ModelTool": MagicMock(return_value=fake_model_tool),
    "aixplain.modules.agent.tool.pipeline_tool": MagicMock(),
    "aixplain.modules.agent.tool.pipeline_tool.PipelineTool": MagicMock(
        return_value=fake_pipeline_tool
    ),
    "aixplain.modules.asset": MagicMock(),
    "aixplain.modules.asset.Asset": MagicMock(),
    "aixplain.utils": MagicMock(),
}

for mod_name, mod_value in _modules.items():
    sys.modules[mod_name] = mod_value
