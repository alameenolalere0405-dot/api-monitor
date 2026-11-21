import os
import tempfile
import unittest
from unittest.mock import patch

import app as pulse


class PulseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database = pulse.DATABASE
        pulse.DATABASE = os.path.join(self.temp_dir.name, "test.db")
        pulse.init_db()
        pulse.app.config["TESTING"] = True
        self.client = pulse.app.test_client()

    def tearDown(self):
        pulse.DATABASE = self.original_database
        self.temp_dir.cleanup()

    @patch("app.validate_public_url", return_value=(True, ""))
    def test_add_endpoint(self, _validate):
        response = self.client.post("/api/endpoints", json={
            "name": "Example",
            "url": "https://example.com"
        })
        self.assertEqual(response.status_code, 201)

    def test_missing_fields_rejected(self):
        response = self.client.post(
            "/api/endpoints", json={"name": "Missing URL"}
        )
        self.assertEqual(response.status_code, 400)

    def test_private_ip_rejected(self):
        with patch("app.socket.getaddrinfo", return_value=[
            (2, 1, 6, "", ("127.0.0.1", 443))
        ]):
            valid, _ = pulse.validate_public_url("https://localhost")
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
