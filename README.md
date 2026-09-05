# cauth

Run Claude Code with a named account. Each account keeps its own login, settings,
and history. Claude handles authentication and refresh.

Requires Python 3.9+ and Claude Code on `PATH`.

## Install

```sh
git clone https://github.com/jhgaylor/cauth.git
cd cauth
mkdir -p "$HOME/.local/bin"
ln -s "$PWD/cauth" "$HOME/.local/bin/cauth"
export PATH="$HOME/.local/bin:$PATH"
```

Keep the clone in place and add the `export` line to your shell startup file.

## Use

```sh
cauth -account work login --email you@company.com
cauth -account personal login --email you@example.com
cauth -account work status
cauth -account work claude -p "explain this repo"
cauth -account personal claude
```

Complete browser authorization once per account. Check `status` to confirm the
account you authorized.

Create a shortcut:

```sh
cauth -account work alias cw
cw -p "explain this repo"
```

Use `cauth list` to list profiles and `cauth -account work logout` to sign out.

See [the usage guide](docs/usage.md) for configuration, shortcut management,
authentication details, and testing.
