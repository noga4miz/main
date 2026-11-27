import shutil
import socket
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKER_AVAILABLE = shutil.which("docker") is not None


@unittest.skipUnless(DOCKER_AVAILABLE, "Docker Compose is required")
class MongoDBComposeTests(unittest.TestCase):
    def run_compose(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["docker", "compose", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_compose_configuration_is_valid(self) -> None:
        result = self.run_compose("config", "--quiet")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mongodb_ping_and_published_port(self) -> None:
        result = self.run_compose(
            "exec",
            "-T",
            "mongodb",
            "mongosh",
            "--quiet",
            "--eval",
            "db.adminCommand({ ping: 1 }).ok",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "1")

        with socket.create_connection(("127.0.0.1", 27017), timeout=2):
            pass


if __name__ == "__main__":
    unittest.main()
