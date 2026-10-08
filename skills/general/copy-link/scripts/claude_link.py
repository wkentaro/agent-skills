import json
import os
import re
import sys
from pathlib import Path
from uuid import UUID


def session_link(session_id, projects):
    session_id = str(UUID(session_id))
    transcript = max(
        projects.glob(f"*/{session_id}.jsonl"),
        key=lambda path: path.stat().st_mtime_ns,
        default=None,
    )
    bridge_id = ""
    if transcript:
        with transcript.open() as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (
                    isinstance(row, dict)
                    and row.get("type") == "bridge-session"
                    and row.get("sessionId") == session_id
                ):
                    bridge_id = row.get("bridgeSessionId", "")
    if isinstance(bridge_id, str) and re.fullmatch(r"(?:cse|session)_[A-Za-z0-9_-]+", bridge_id):
        return "https://claude.ai/code/" + re.sub(r"^cse_", "session_", bridge_id)
    return f"claude://resume?session={session_id}"


if __name__ == "__main__":
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    print(session_link(sys.argv[1], config / "projects"))
