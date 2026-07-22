import time
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.verification_store import InMemoryVerificationCodeStore  # noqa: E402


class InMemoryVerificationCodeStoreTests(unittest.TestCase):
    def test_round_trip_and_delete(self):
        store = InMemoryVerificationCodeStore()
        store.setex("verification_code:user@example.com", 60, "123456")

        self.assertEqual(
            "123456",
            store.get("verification_code:user@example.com"),
        )
        store.delete("verification_code:user@example.com")
        self.assertIsNone(store.get("verification_code:user@example.com"))

    def test_expired_code_is_removed(self):
        store = InMemoryVerificationCodeStore()
        store.setex("verification_code:expired", 0, "654321")
        time.sleep(0.001)

        self.assertIsNone(store.get("verification_code:expired"))


if __name__ == "__main__":
    unittest.main()
