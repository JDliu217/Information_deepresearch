import unittest

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.main import create_app
from app.api.schemas import ResearchRequest


class ApiAppTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self):
        client = TestClient(create_app())

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_research_request_validates_non_empty_query(self):
        with self.assertRaises(ValidationError):
            ResearchRequest(query="")



if __name__ == "__main__":
    unittest.main()
