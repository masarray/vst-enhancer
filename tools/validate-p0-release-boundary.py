#!/usr/bin/env python3
"""Validate the public-only P0 release security boundary."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-macos-and-publish.yml"
UPDATER = ROOT / "tools" / "update-public-crossplatform-release.py"


def fail(message: str) -> None:
    raise SystemExit(f"[FAILED] {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def section(text: str, start: str, end: str | None = None) -> str:
    begin = text.find(start)
    require(begin >= 0, f"Missing section marker: {start}")
    if end is None:
        return text[begin:]
    finish = text.find(end, begin + len(start))
    require(finish >= 0, f"Missing section marker: {end}")
    return text[begin:finish]


def main() -> int:
    require(WORKFLOW.is_file(), "Approved public release workflow is missing.")
    require(UPDATER.is_file(), "Public metadata updater is missing.")
    text = WORKFLOW.read_text(encoding="utf-8")

    require(text.count("\n  build-macos:\n") == 1, "Expected one build-macos job.")
    require(text.count("\n  publish-release:\n") == 1, "Expected one publish-release job.")
    build = section(text, "\n  build-macos:\n", "\n  publish-release:\n")
    publish = section(text, "\n  publish-release:\n")

    require("permissions:\n      contents: read" in build, "Build job must be contents-read.")
    require("permissions:\n      actions: read\n      contents: write" in publish, "Publish job permissions changed.")
    require("${{ secrets.ASKP_PRIVATE_SOURCE_TOKEN }}" in build, "Private source token is missing from build job.")
    require("ASKP_PRIVATE_SOURCE_TOKEN" not in publish, "Private source token reached publish job.")
    require("PRIVATE_REPO:" not in publish, "Private repository identity reached publish job.")
    require("gh repo clone \"$PRIVATE_REPO\"" not in publish, "Publish job clones the private repository.")
    require("helper/scripts/" not in publish, "Publish job executes private helper tooling.")

    require("helperCommit" in build, "Approved helper SHA is not required.")
    require("actual_helper" in build and "== \"$helper_commit\"" in build, "Helper SHA is not verified.")
    require("rm -rf helper source private" in build, "Private checkout cleanup is missing.")
    require("HANDOFF-SHA256SUMS.txt" in build and "HANDOFF-SHA256SUMS.txt" in publish, "Handoff integrity gate is missing.")
    require("actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in build, "Upload action is not pinned.")
    require("actions/download-artifact@37930b1c2abaa49bbe596cd826c3c89aef350131" in publish, "Download action is not pinned.")
    require("public/tools/update-public-crossplatform-release.py" in publish, "Publish job does not use public tooling.")

    prohibited = re.compile(r"\\\.\(c\|cc\|cpp\|cxx\|h\|hh\|hpp")
    require(prohibited.search(build) is not None, "Build handoff source-extension gate is missing.")
    require(prohibited.search(publish) is not None, "Publish handoff source-extension gate is missing.")

    print("[PASS] Public build is read-only; publish is source-free; private Actions remain unnecessary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
