import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from workflows.game_gen_workflow import get_llm  # noqa: E402


class LlmConfigurationTests(unittest.TestCase):
    def tearDown(self):
        get_llm.cache_clear()

    def test_openai_default_uses_current_balanced_model(self):
        with (
            patch.dict(
                os.environ,
                {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
                clear=True,
            ),
            patch("workflows.game_gen_workflow.ChatOpenAI") as chat_openai,
        ):
            get_llm.cache_clear()
            get_llm()

        options = chat_openai.call_args.kwargs
        self.assertEqual("gpt-5.6-terra", options["model"])
        self.assertEqual("none", options["reasoning_effort"])
        self.assertNotIn("temperature", options)

    def test_legacy_openai_override_preserves_temperature(self):
        with (
            patch.dict(
                os.environ,
                {
                    "LLM_PROVIDER": "openai",
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_MODEL": "gpt-4o",
                },
                clear=True,
            ),
            patch("workflows.game_gen_workflow.ChatOpenAI") as chat_openai,
        ):
            get_llm.cache_clear()
            get_llm()

        options = chat_openai.call_args.kwargs
        self.assertEqual(0.2, options["temperature"])
        self.assertNotIn("reasoning_effort", options)

    def test_provider_defaults_use_current_stable_model_ids(self):
        providers = (
            ("deepseek", "DEEPSEEK_API_KEY", "deepseek-v4-flash"),
            ("qwen", "QWEN_API_KEY", "qwen3.7-plus"),
        )
        for provider, key_name, expected_model in providers:
            with self.subTest(provider=provider):
                with (
                    patch.dict(
                        os.environ,
                        {"LLM_PROVIDER": provider, key_name: "test-key"},
                        clear=True,
                    ),
                    patch("workflows.game_gen_workflow.ChatOpenAI") as chat_openai,
                ):
                    get_llm.cache_clear()
                    get_llm()

                self.assertEqual(expected_model, chat_openai.call_args.kwargs["model"])


if __name__ == "__main__":
    unittest.main()
