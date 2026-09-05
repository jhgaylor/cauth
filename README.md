# cauth

`cauth` selects a named Claude Code profile for one invocation. Requires
Python 3.9+ and Claude Code on `PATH`. It uses `CLAUDE_CONFIG_DIR`; Claude handles
OAuth login, credential storage, and refresh. It doesn't extract tokens or
switch accounts when a command hits a usage limit.

Clone the repository and make the executable available in your current shell:

```sh
git clone https://github.com/jhgaylor/cauth.git
cd cauth
export PATH="$PWD:$PATH"
cauth -account first-account login --email first@example.com
cauth -account second-account login --email second@example.com
cauth -account third-account login --email third@example.com
cauth -account first-account status
cauth -account first-account claude -p "my prompt"
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
ln -s "$PWD/cauth" "$HOME/.local/bin/cauth"
```

Run that command from the cloned repository and keep the clone in place.
Ensure `~/.local/bin` is on your shell's `PATH`. The symlink command deliberately
fails if a launcher with that name already exists.

Create a shortcut for an account:

```sh
cauth -account first-account alias c1
cauth -account second-account alias c2
export PATH="$HOME/.local/bin:$PATH"
c1 -p "my prompt"
c2 -p "another prompt"
```

These are executable launchers, so they work in zsh, bash, and other shells.
They forward all arguments to `claude` using the selected account; `c1` alone
starts an interactive session, and `c1 auth status` checks its login. Install
one after creating the account profile with `login`. Set `CAUTH_BIN_DIR` to an
absolute directory to install somewhere other than `~/.local/bin`. Add that
directory to your shell startup file's PATH for use in new terminals.

An alias stores the account name, profile root, and absolute paths to this
checkout's launcher and Python interpreter. Keep the checkout and interpreter
in place. It contains no tokens. Existing files, symlinks, and executable names
on PATH are never overwritten; shell functions and shell aliases cannot be
detected by this process. To remove a shortcut, delete its installed file
(e.g. `rm ~/.local/bin/c1`), then recreate it if changing the account or location.

Profiles default to `~/.config/cauth/accounts/NAME`, respecting
`XDG_CONFIG_HOME`. `CAUTH_HOME` overrides the root. Keep this path stable:
Claude also derives its macOS Keychain entry from the config directory.
Existing `~/.config/ournewcli` profiles are reused when the new default root
is absent, and `OURNEWCLI_HOME` remains a fallback for `CAUTH_HOME`. Existing
logins therefore keep their original paths after the rename.
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
