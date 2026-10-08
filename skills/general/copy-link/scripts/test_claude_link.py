import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from claude_link import session_link


def test_session_link():
    session_id = "00000000-0000-4000-8000-000000000001"
    desktop = f"claude://resume?session={session_id}"
    with TemporaryDirectory() as directory:
        projects = Path(directory)
        assert session_link(session_id, projects) == desktop
        project = projects / "project"
        project.mkdir()
        transcript = project / f"{session_id}.jsonl"
        metadata = {"type": "bridge-session", "sessionId": session_id}
        for bridge_id in ("cse_example123", "session_example123"):
            transcript.write_text(
                json.dumps({**metadata, "bridgeSessionId": bridge_id}) + '\n{"partial":'
            )
            assert session_link(session_id, projects) == "https://claude.ai/code/session_example123"
        transcript.write_text(
            json.dumps({**metadata, "bridgeSessionId": "cse_old"}) + "\n"
            + json.dumps({**metadata, "bridgeSessionId": ""}) + "\n"
            + json.dumps({**metadata, "sessionId": "another-session", "bridgeSessionId": "cse_other"})
        )
        assert session_link(session_id, projects) == desktop
        transcript.write_text(json.dumps({**metadata, "bridgeSessionId": "cse_invalid?token=secret"}))
        assert session_link(session_id, projects) == desktop
        transcript.write_text('[]\nnull\n{"type":"user"}\n')
        assert session_link(session_id, projects) == desktop
        other_project = projects / "other-project"
        other_project.mkdir()
        newer = other_project / transcript.name
        newer.write_text(json.dumps({**metadata, "bridgeSessionId": "cse_latest"}))
        os.utime(transcript, ns=(1, 1))
        assert session_link(session_id, projects) == "https://claude.ai/code/session_latest"
        # Exercise the CLI with a separate config directory, without real session data.
        config = projects / "config"
        cli_project = config / "projects" / "project"
        cli_project.mkdir(parents=True)
        (cli_project / transcript.name).write_text(newer.read_text())
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("claude_link.py")), session_id],
            env={**os.environ, "CLAUDE_CONFIG_DIR": str(config)},
            check=True, capture_output=True, text=True,
        )
        assert result.stdout.strip() == "https://claude.ai/code/session_latest"
        try:
            session_link("../../another-session", projects)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid session IDs must be rejected")


if __name__ == "__main__":
    test_session_link()
    print("Session link checks passed.")
