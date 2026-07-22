import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from modules.generated_artifact import (  # noqa: E402
    MAX_FILE_BYTES,
    ArtifactValidationError,
    GeneratedArtifact,
)


class GeneratedArtifactTests(unittest.TestCase):
    def test_valid_nested_files_are_deployed(self):
        artifact = GeneratedArtifact.from_mapping(
            {
                "index.html": "<script src='js/game.js'></script>",
                "js\\game.js": "console.log('ready')",
            }
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deployed = artifact.deploy(root, "project_7_safe")

            self.assertEqual(root.resolve(), deployed.parent)
            self.assertTrue((deployed / "index.html").is_file())
            self.assertEqual(
                "console.log('ready')",
                (deployed / "js" / "game.js").read_text(encoding="utf-8"),
            )

    def test_path_traversal_and_absolute_paths_are_rejected(self):
        unsafe_paths = (
            "../outside.html",
            "assets/../../outside.js",
            "/tmp/index.html",
            "C:\\temp\\index.html",
        )
        for unsafe_path in unsafe_paths:
            with self.subTest(path=unsafe_path):
                with self.assertRaises(ArtifactValidationError):
                    GeneratedArtifact.from_mapping(
                        {"index.html": "safe", unsafe_path: "unsafe"}
                    )

    def test_hidden_reserved_and_duplicate_paths_are_rejected(self):
        invalid_file_sets = (
            {"index.html": "safe", ".env": "secret"},
            {"index.html": "safe", "assets/CON.txt": "reserved"},
            {"index.html": "safe", "assets/game.js:stream": "alternate data"},
            {"index.html": "safe", "assets/game?.js": "invalid character"},
            {"index.html": "safe", "js/game.js": "a", "js\\game.js": "b"},
        )
        for files in invalid_file_sets:
            with self.subTest(files=files):
                with self.assertRaises(ArtifactValidationError):
                    GeneratedArtifact.from_mapping(files)

    def test_entrypoint_and_size_limits_are_enforced(self):
        with self.assertRaises(ArtifactValidationError):
            GeneratedArtifact.from_mapping({"game.js": "console.log('missing')"})

        with self.assertRaises(ArtifactValidationError):
            GeneratedArtifact.from_mapping(
                {"index.html": "x" * (MAX_FILE_BYTES + 1)}
            )


if __name__ == "__main__":
    unittest.main()
