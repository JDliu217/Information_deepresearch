import unittest

from app.core.run_control import (
    CANCELLED,
    CANCEL_REQUESTED,
    COMPLETED,
    InMemoryRunControlStore,
    RedisRunControlStore,
)


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expirations = {}

    def set(self, key, value, *, ex):
        self.values[key] = value
        self.expirations[key] = ex

    def get(self, key):
        return self.values.get(key)

    def exists(self, key):
        return int(key in self.values)

    def delete(self, key):
        self.values.pop(key, None)


class RunControlTests(unittest.TestCase):
    def test_in_memory_store_tracks_status_and_cancel_request(self):
        store = InMemoryRunControlStore()

        started = store.start("session-1")
        self.assertEqual(started.status, "running")
        updated = store.update("session-1", phase="researching", iteration=1)
        self.assertEqual(updated.phase, "researching")

        requested = store.request_cancel("session-1")
        self.assertEqual(requested.status, CANCEL_REQUESTED)
        self.assertTrue(store.is_cancel_requested("session-1"))

        cancelled = store.mark_cancelled("session-1", phase="researching", iteration=1)
        self.assertEqual(cancelled.status, CANCELLED)
        self.assertFalse(store.is_cancel_requested("session-1"))

    def test_start_clears_previous_cancel_request(self):
        store = InMemoryRunControlStore()
        store.request_cancel("session-2")
        store.start("session-2")
        self.assertFalse(store.is_cancel_requested("session-2"))
        self.assertEqual(store.get("session-2").status, "running")

    def test_redis_store_serializes_status_and_uses_expiration(self):
        client = FakeRedis()
        store = RedisRunControlStore(client=client, ttl_seconds=60)

        completed = store.mark_completed("session-3", phase="completed", iteration=2)
        self.assertEqual(store.get("session-3"), completed)
        self.assertEqual(client.expirations["information_deepresearch:run:session-3:status"], 60)

        requested = store.request_cancel("session-3")
        self.assertEqual(requested.status, CANCEL_REQUESTED)
        self.assertTrue(store.is_cancel_requested("session-3"))

        store.mark_completed("session-3", phase="completed", iteration=2)
        self.assertFalse(store.is_cancel_requested("session-3"))
        self.assertEqual(store.get("session-3").status, COMPLETED)


if __name__ == "__main__":
    unittest.main()
