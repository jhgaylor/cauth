# Local Claude accounts

`ournewcli` selects a named Claude Code profile for one invocation. Requires
Python 3.9+ and Claude Code on `PATH`. It uses `CLAUDE_CONFIG_DIR`; Claude handles
OAuth login, credential storage, and refresh. It doesn't extract tokens or
switch accounts when a command hits a usage limit.

Clone the repository and make the executable available in your current shell:

```sh
git clone https://github.com/jhgaylor/claude-accounts.git
cd claude-accounts
export PATH="$PWD:$PATH"
ournewcli -account first-account login --email first@example.com
ournewcli -account second-account login --email second@example.com
ournewcli -account third-account login --email third@example.com
ournewcli -account first-account status
ournewcli -account first-account claude -p "my prompt"
```

Complete Claude's browser authorization once for each profile. The email flag
prefills the login page; verify the account you authorize if your browser is
already signed in. You can use the same browser for these logins. Subsequent
CLI invocations reuse the saved login. Re-run `login` if Claude asks you to
reauthenticate. `status` delegates to `claude auth status`, so check it after
each initial login. `logout` delegates to `claude auth logout` for that profile.
`list` shows profile names (including profiles with incomplete or expired login).

To install the launcher permanently, symlink it into a directory on your PATH:

```sh
mkdir -p "$HOME/.local/bin"
ln -s "$PWD/ournewcli" "$HOME/.local/bin/ournewcli"
```

Run that command from the cloned repository and keep the clone in place.
Ensure `~/.local/bin` is on your shell's `PATH`. The symlink command deliberately
fails if a launcher with that name already exists.

Profiles default to `~/.config/ournewcli/accounts/NAME`, respecting
`XDG_CONFIG_HOME`. `OURNEWCLI_HOME` overrides the root. Keep this path stable:
Claude also derives its macOS Keychain entry from the config directory.
Directories are created with private permissions. The launcher never reads
credentials, and leaves your default Claude profile untouched.

Each profile has separate user settings, history, plugins, and memory. Project
and managed settings still apply. This is account selection, not a security
sandbox: project settings, explicit Claude arguments, API-key helpers, gateway
sessions, or other provider configuration can affect authentication. Keep these
profiles configured for subscription login and use `status` to verify. Known
environment auth/routing overrides are rejected by name without printing their
values; unset them in the invoking shell. `CLAUDE_CONFIG_DIR` itself is replaced
with the selected profile for the child process only.

The executable replaces itself with Claude, preserving your working directory,
terminal, stdin/stdout/stderr, signals, and Claude's exit status. Arguments after
`claude` are forwarded verbatim. Separate account invocations can run in parallel.

Validation:

```sh
python3 -m unittest discover -s . -p 'test_*.py'
```

Tests use a fake Claude executable and temporary directories to check account
isolation, concurrent selection, argument/stdin forwarding, exit codes, private
directories, and credential-override handling without contacting Anthropic.
Real subscription login must be completed interactively by the account owner.

References:
- [Configuration directory](https://code.claude.com/docs/en/env-vars)
- [Credential storage and authentication](https://code.claude.com/docs/en/authentication)
