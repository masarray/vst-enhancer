#!/usr/bin/env python3
"""Validate the public release and GitHub Pages security boundary."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
RELEASE_WORKFLOW = WORKFLOWS / "build-macos-and-publish.yml"
PAGES_WORKFLOW = WORKFLOWS / "pages.yml"
UPDATER = ROOT / "tools" / "update-public-crossplatform-release.py"

APPROVED_WORKFLOWS = [
    ".github/workflows/build-macos-and-publish.yml",
    ".github/workflows/pages.yml",
]


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


def validate_workflow_inventory() -> None:
    actual = sorted(
        path.relative_to(ROOT).as_posix()
        for path in WORKFLOWS.iterdir()
        if path.is_file() and path.suffix in {".yml", ".yaml"}
    )
    require(
        actual == APPROVED_WORKFLOWS,
        f"Workflow allowlist mismatch: expected {APPROVED_WORKFLOWS}, got {actual}",
    )


def validate_release_workflow(text: str) -> None:
    require(text.count("\n  build-macos:\n") == 1, "Expected one build-macos job.")
    require(
        text.count("\n  publish-release:\n") == 1,
        "Expected one publish-release job.",
    )
    build = section(text, "\n  build-macos:\n", "\n  publish-release:\n")
    publish = section(text, "\n  publish-release:\n")

    require(
        "permissions:\n      contents: read" in build,
        "Build job must remain contents-read.",
    )
    require(
        "permissions:\n      actions: write\n      contents: write" in publish,
        "Publish job must have only actions-write and contents-write.",
    )
    require(
        "${{ secrets.ASKP_PRIVATE_SOURCE_TOKEN }}" in build,
        "Private source token is missing from build job.",
    )
    require(
        "ASKP_PRIVATE_SOURCE_TOKEN" not in publish,
        "Private source token reached publish job.",
    )
    require("PRIVATE_REPO:" not in publish, "Private repository identity reached publish job.")
    require(
        "gh repo clone \"$PRIVATE_REPO\"" not in publish,
        "Publish job clones the private repository.",
    )
    require(
        "helper/scripts/" not in publish,
        "Publish job executes private helper tooling.",
    )

    require("helperCommit" in build, "Approved helper SHA is not required.")
    require(
        "actual_helper" in build and "== \"$helper_commit\"" in build,
        "Helper SHA is not verified.",
    )
    require(
        "rm -rf helper source private" in build,
        "Private checkout cleanup is missing.",
    )
    require(
        "HANDOFF-SHA256SUMS.txt" in build
        and "HANDOFF-SHA256SUMS.txt" in publish,
        "Handoff integrity gate is missing.",
    )
    require(
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
        in build,
        "Upload action is not pinned.",
    )
    require(
        "actions/download-artifact@37930b1c2abaa49bbe596cd826c3c89aef350131"
        in publish,
        "Download action is not pinned.",
    )
    require(
        "public/tools/update-public-crossplatform-release.py" in publish,
        "Publish job does not use public tooling.",
    )

    prohibited = re.compile(r"\\\.\(c\|cc\|cpp\|cxx\|h\|hh\|hpp")
    require(
        prohibited.search(build) is not None,
        "Build handoff source-extension gate is missing.",
    )
    require(
        prohibited.search(publish) is not None,
        "Publish handoff source-extension gate is missing.",
    )

    require(
        "APPROVED_PAGES_WORKFLOW: .github/workflows/pages.yml" in build,
        "Pages workflow is absent from the release allowlist.",
    )
    require(
        "approved_workflows=" in build,
        "Release workflow inventory is not compared with an allowlist.",
    )
    require(
        "PAGES_WORKFLOW: pages.yml" in publish,
        "Publish job does not identify the approved Pages workflow.",
    )
    require(
        '[[ "$build_type" == workflow ]]' in publish,
        "Release does not require Pages workflow mode.",
    )
    require(
        'gh workflow run "$PAGES_WORKFLOW"' in publish,
        "Release does not dispatch the Pages workflow.",
    )
    require(
        '-f site_ref="$PUBLIC_METADATA_COMMIT"' in publish,
        "Pages dispatch is not pinned to the public metadata commit.",
    )
    require(
        '-f expected_version="$RELEASE_TAG"' in publish,
        "Pages dispatch does not carry the expected release version.",
    )
    require(
        "python3 public/tools/validate-live-seo.py" in publish,
        "Release does not verify the deployed site before publication.",
    )
    require(
        "gh-pages" not in text,
        "Legacy gh-pages deployment logic remains in the release workflow.",
    )


def validate_pages_workflow(text: str) -> None:
    require("\n  pull_request:\n" in text, "Pages pull-request validation is missing.")
    require("\n  push:\n" in text, "Pages push deployment trigger is missing.")
    require("\n  workflow_dispatch:\n" in text, "Pages release handoff trigger is missing.")
    require(text.count("\n  validate:\n") == 1, "Expected one Pages validation job.")
    require(text.count("\n  deploy:\n") == 1, "Expected one Pages deployment job.")

    validate = section(text, "\n  validate:\n", "\n  deploy:\n")
    deploy = section(text, "\n  deploy:\n")

    require(
        "python3 tools/validate-p0-release-boundary.py" in validate,
        "Pages validation does not enforce the release boundary.",
    )
    require(
        "python3 tools/validate-seo.py" in validate,
        "Pages validation does not enforce the SEO contract.",
    )
    require(
        "github.event_name != 'pull_request'" in deploy,
        "Pull requests are not blocked from deployment.",
    )
    require(
        "permissions:\n      contents: read\n      pages: write\n      id-token: write"
        in deploy,
        "Pages deployment permissions changed.",
    )
    require(
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
        in text,
        "Pages checkout action is not pinned.",
    )
    require(
        "actions/configure-pages@45bfe0192ca1faeb007ade9deae92b16b8254a0d"
        in deploy,
        "configure-pages action is not pinned.",
    )
    require(
        "actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9"
        in deploy,
        "upload-pages-artifact action is not pinned.",
    )
    require(
        "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128"
        in deploy,
        "deploy-pages action is not pinned.",
    )
    require(
        "site_ref must be an exact 40-character commit SHA" in validate,
        "Exact Pages source validation is missing.",
    )
    require(
        "--expected-version" in deploy,
        "Live Pages version validation is missing.",
    )
    require(
        "gh-pages" not in text,
        "Legacy gh-pages references remain in the Pages workflow.",
    )


def main() -> int:
    require(RELEASE_WORKFLOW.is_file(), "Approved public release workflow is missing.")
    require(PAGES_WORKFLOW.is_file(), "Approved Pages workflow is missing.")
    require(UPDATER.is_file(), "Public metadata updater is missing.")

    validate_workflow_inventory()
    validate_release_workflow(RELEASE_WORKFLOW.read_text(encoding="utf-8"))
    validate_pages_workflow(PAGES_WORKFLOW.read_text(encoding="utf-8"))

    print(
        "[PASS] Public build is read-only; publish is source-free; "
        "Pages is exact-source validated; workflow inventory is allowlisted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
