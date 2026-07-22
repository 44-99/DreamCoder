import os
import sys
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.dependencies import Base, get_db, get_verification_store  # noqa: E402
from core.verification_store import InMemoryVerificationCodeStore  # noqa: E402
from routers.auth import router as auth_router  # noqa: E402


class LocalAuthFlowTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        sessions = sessionmaker(bind=engine)
        store = InMemoryVerificationCodeStore()

        def override_db():
            with sessions() as db:
                yield db

        def override_store():
            yield store

        app = FastAPI()
        app.include_router(auth_router)
        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_verification_store] = override_store
        self.client = TestClient(app)

    def test_console_verification_register_and_login(self):
        previous_mode = os.environ.get("AUTH_DELIVERY_MODE")
        previous_environment = os.environ.get("ENVIRONMENT")
        os.environ["AUTH_DELIVERY_MODE"] = "console"
        os.environ["ENVIRONMENT"] = "development"
        try:
            verification = self.client.post(
                "/auth/verification",
                json={"email": "player@example.com"},
            )
            self.assertEqual(200, verification.status_code)
            code = verification.json()["dev_code"]

            registration = self.client.post(
                "/auth/register",
                json={
                    "username": "player",
                    "password": "secret123",
                    "email": "player@example.com",
                    "verificationCode": code,
                },
            )
            self.assertEqual(200, registration.status_code)
            self.assertIn("access_token", registration.json())

            login = self.client.post(
                "/auth/login",
                json={"username": "player", "password": "secret123"},
            )
            self.assertEqual(200, login.status_code)
            self.assertIn("access_token", login.json())
        finally:
            if previous_mode is None:
                os.environ.pop("AUTH_DELIVERY_MODE", None)
            else:
                os.environ["AUTH_DELIVERY_MODE"] = previous_mode
            if previous_environment is None:
                os.environ.pop("ENVIRONMENT", None)
            else:
                os.environ["ENVIRONMENT"] = previous_environment


if __name__ == "__main__":
    unittest.main()
