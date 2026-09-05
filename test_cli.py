import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("ournewcli")


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.bin = self.base / "bin"
        self.bin.mkdir()
        fake = self.bin / "claude"
        fake.write_text("#!" + sys.executable + "\n" + '''
import json, os, sys
from pathlib import Path
p = Path(os.environ["CLAUDE_CONFIG_DIR"])
if sys.argv[1:3] == ["auth", "login"]:
    (p / "fixture-login").write_text(p.name)
print(json.dumps({"args": sys.argv[1:], "profile": str(p),
                  "login": (p / "fixture-login").read_text(),
                  "cwd": os.getcwd(), "stdin": sys.stdin.read()}))
sys.exit(int(os.environ.get("FIXTURE_EXIT", "0")))
''')
        fake.chmod(0o700)
        self.env = {"PATH": str(self.bin), "HOME": str(self.base),
                    "OURNEWCLI_HOME": str(self.base / "profiles")}

    def call(self, *args, env=None, input=""):
        return subprocess.run([sys.executable, str(CLI), *args],
                              env=env or self.env, cwd=self.base,
                              input=input, capture_output=True, text=True)

    def login(self, name):
        result = self.call("-account", name, "login")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_profiles_remain_isolated_in_parallel(self):
        for name in ("first", "second", "third"):
            self.login(name)
        def run(name):
            return json.loads(self.call("-account", name, "claude", "-p", "hi").stdout)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(run, ["first", "second", "third", "first"]))
        self.assertEqual([r["login"] for r in results], ["first", "second", "third", "first"])
        self.assertFalse((self.base / ".claude").exists())

    def test_arguments_stdin_cwd_and_exit_status(self):
        self.login("first")
        prompt = 'hello "quoted"; $(touch should-not-exist)\nsecond line'
        result = self.call("-a", "first", "claude", "-p", prompt,
                           env={**self.env, "FIXTURE_EXIT": "42"}, input="piped input")
        self.assertEqual(result.returncode, 42)
        data = json.loads(result.stdout)
        self.assertEqual(data["args"], ["-p", prompt])
        self.assertEqual(data["stdin"], "piped input")
        self.assertEqual(Path(data["cwd"]).resolve(), self.base.resolve())
        self.assertFalse((self.base / "should-not-exist").exists())

    def test_auth_overrides_fail_without_exposing_values(self):
        for key in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_BASE_URL",
                    "CLAUDE_CODE_USE_BEDROCK", "ANTHROPIC_PROFILE"):
            result = self.call("-account", "first", "login", env={**self.env, key: "SECRET"})
            self.assertEqual(result.returncode, 2)
            self.assertIn(key, result.stderr)
            self.assertNotIn("SECRET", result.stdout + result.stderr)

    def test_names_and_unknown_accounts(self):
        for name in ("../escape", "/tmp/escape", "a/b", "", "..", "a" * 65):
            self.assertEqual(self.call("-account", name, "login").returncode, 2)
        self.assertEqual(self.call("-account", "typo", "claude", "-p", "hi").returncode, 2)
        self.assertFalse((self.base / "profiles").exists())

    def test_permissions_and_symlinks(self):
        data = self.login("first")
        profile = Path(data["profile"])
        self.assertEqual(profile.stat().st_mode & 0o777, 0o700)
        (profile.parent / "alias").symlink_to(profile, target_is_directory=True)
        self.assertEqual(self.call("-account", "alias", "status").returncode, 2)
        profile.chmod(0o755)
        self.assertEqual(self.call("-account", "first", "status").returncode, 2)

    def test_management_and_config_override(self):
        self.assertEqual(self.call("list").stdout, "")
        result = self.call("--account", "first", "login", "--email", "one@example.com",
                           env={**self.env, "CLAUDE_CONFIG_DIR": str(self.base / "other")})
        self.assertEqual(json.loads(result.stdout)["args"],
                         ["auth", "login", "--claudeai", "--email", "one@example.com"])
        self.assertFalse((self.base / "other").exists())
        for command in ("status", "logout"):
            self.assertEqual(json.loads(self.call("-a", "first", command).stdout)["args"], ["auth", command])
        self.assertEqual(self.call("list").stdout, "first\n")

    def test_missing_binary_and_invalid_invocations(self):
        (self.bin / "claude").unlink()
        self.assertEqual(self.call("-a", "first", "login").returncode, 127)
        for args in (("-a",), ("-a", "first"), ("-a", "first", "status", "extra"),
                     ("-a", "first", "login", "--email")):
            self.assertEqual(self.call(*args).returncode, 2)


if __name__ == "__main__":
    unittest.main()
