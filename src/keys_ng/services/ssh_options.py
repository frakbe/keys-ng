from __future__ import annotations

import shlex


class SSHOptionsError(ValueError):
    pass


def parse_ssh_options(text: str) -> list[str]:
    """Parse user-entered SSH options into argv without involving a shell.

    The destination, username, port and X11 forwarding are managed separately by
    Keys NG.  We therefore reject options that would silently override those
    fields.  All other OpenSSH options (including -J, -L, -R, -D and -o ...) are
    passed through as argv tokens.
    """
    text = text.strip()
    if not text:
        return []
    try:
        argv = shlex.split(text, posix=True)
    except ValueError as exc:
        raise SSHOptionsError(f"Invalid SSH options: {exc}") from exc
    validate_ssh_options(argv)
    return argv


def validate_ssh_options(argv: list[str]) -> None:
    for token in argv:
        if token == "--":
            raise SSHOptionsError("SSH advanced options cannot contain --")
        if token in {"-X", "-Y", "-x"}:
            raise SSHOptionsError("Use the dedicated X11 forwarding selector instead of -X/-Y/-x")
        if token in {"-p", "-l"} or token.startswith("-p=") or token.startswith("-l="):
            raise SSHOptionsError("Port and username are managed by their dedicated fields")
        if token.startswith("-p") and len(token) > 2 and token[2:].isdigit():
            raise SSHOptionsError("Port is managed by its dedicated field")
        if token.startswith("-l") and len(token) > 2:
            raise SSHOptionsError("Username is managed by its dedicated field")

    # Also prevent the -o form from overriding the dedicated destination fields.
    for index, token in enumerate(argv):
        option_value = None
        if token == "-o" and index + 1 < len(argv):
            option_value = argv[index + 1]
        elif token.startswith("-o") and len(token) > 2:
            option_value = token[2:]
        if option_value:
            key = option_value.split("=", 1)[0].strip().lower()
            if key in {"port", "user"}:
                raise SSHOptionsError("Port and username are managed by their dedicated fields")


def format_ssh_options(argv: list[str]) -> str:
    """Return a safely quoted, editable representation of stored argv tokens."""
    return shlex.join(argv)
