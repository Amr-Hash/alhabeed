from django.test import TestCase
from django.test.client import Client


class HealthEndpointTests(TestCase):
    def test_health_reports_migration_head_ok(self):
        response = Client().get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["migration_head_ok"])
        self.assertEqual(payload["pending_migrations"], [])
