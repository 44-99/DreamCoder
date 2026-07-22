import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from workflows.game_gen_workflow import (  # noqa: E402
    deployment_node,
    test_validator_node as validate_generated_artifact,
)


class ArtifactWorkflowTests(unittest.TestCase):
    def test_validation_error_skips_deployment(self):
        escape_name = f"dreamcoder_escape_{uuid4().hex}.txt"
        state = {
            "user_id": 17,
            "generated_files": {
                "index.html": "<canvas></canvas>",
                f"../{escape_name}": "must not be written",
            },
            "logs": [],
            "error": None,
        }

        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory).parent / escape_name
            with patch.dict(os.environ, {"PROJECTS_DIR": directory}):
                state = asyncio.run(validate_generated_artifact(state))
                state = asyncio.run(deployment_node(state))

            self.assertIn("生成产物校验失败", state["error"])
            self.assertIsNone(state.get("deployment_url"))
            self.assertEqual("skipped", state["logs"][-1]["status"])
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
