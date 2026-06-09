import unittest

from melodious_v2.deployment.smoke import run_local_testclient_smoke


class DeploymentSmokeTests(unittest.TestCase):
    def test_local_public_demo_smoke_downloads_artifacts(self):
        result = run_local_testclient_smoke()

        self.assertTrue(result["passed"])
        self.assertEqual(result["health"]["status"], "ok")
        self.assertEqual(result["version"]["schema_version"], "2.0")
        self.assertEqual(result["sample_transcription"]["status"], "complete")
        self.assertEqual(result["sample_transcription"]["sample_id"], "sample-notation-1")
        artifact_types = {artifact["artifact_type"] for artifact in result["artifact_downloads"]}
        self.assertEqual(artifact_types, {"musicxml", "midi"})
        for artifact in result["artifact_downloads"]:
            self.assertGreater(artifact["byte_count"], 0)
            self.assertEqual(len(artifact["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
