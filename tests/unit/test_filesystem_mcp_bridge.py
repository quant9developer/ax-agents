from pathlib import Path

from enterprise_ai_platform.mcp.filesystem_bridge import _resolve_path


def test_resolve_path_keeps_workspace_relative_file() -> None:
    resolved = _resolve_path("examples/demo/quarterly_update_ko.txt")

    assert resolved.name == "quarterly_update_ko.txt"
    assert resolved.is_absolute()
    assert Path.cwd() in resolved.parents
