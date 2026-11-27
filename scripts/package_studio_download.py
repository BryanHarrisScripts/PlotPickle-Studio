#!/usr/bin/env python3
"""Build the public PlotPickle Studio ZIP from the checked-out Git source."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ("plugin.json", ".codex-plugin/plugin.json")
FILES = (
    *MANIFESTS, ".mcp.json", "LICENSE", "docs/pitch-edit-standard-v1.md",
    "assets/composer-icon.png", "assets/plotpickle-logo.png", "assets/studio-logo.png",
    "assets/studio-composer-icon.png", "assets/plotpickle-architecture.png",
    "assets/branding-locked/composer-icon.png", "assets/branding-locked/locked-branding.json",
    "assets/branding-locked/listing-icon-256.png", "assets/branding-locked/studio-logo-approved.png",
)

SOURCE_ONLY = {
    "skills/plotpickle-editor/windows/fixtures/editor-seed.synthetic.json",
    "skills/plotpickle-editor/windows/test_seed_fixture.py",
    "skills/plotpickle-story-flow/scripts/test-verify-portable-package.py",
}


def tracked_skills():
    listing = subprocess.check_output(["git", "ls-files", "-z", "--", "skills"], cwd=ROOT)
    return {name for name in listing.decode().split("\0") if name} - SOURCE_ONLY


def check_endpoint(url, scopes):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.port
            or parsed.path != "/mcp" or parsed.query or parsed.fragment
            or not (parsed.hostname.endswith(".chatgpt.site") or parsed.hostname.endswith(".plotpickle.com"))):
        raise ValueError("Expected a canonical HTTPS PlotPickle Studio MCP URL")
    expected = f'{parsed.scheme}://{parsed.netloc}/.well-known/oauth-protected-resource/mcp'
    headers = subprocess.check_output(
        ["curl", "-sS", "--max-time", "20", "-D", "-", "-o", os.devnull, "-w", "%{http_code}", url],
        text=True,
    ).splitlines()
    challenge = next((line.split(":", 1)[1].strip() for line in headers
                      if line.lower().startswith("www-authenticate:")), "")
    if headers[-1] != "401" or not challenge.startswith("Bearer ") or f'resource_metadata="{expected}"' not in challenge:
        raise ValueError("Studio MCP returned an unexpected OAuth challenge")
    metadata = json.loads(subprocess.check_output(
        ["curl", "-fsS", "--max-time", "20", expected], text=True,
    ))
    if metadata.get("resource") != url or not set(scopes).issubset(metadata.get("scopes_supported", [])):
        raise ValueError("Studio OAuth metadata does not match the packaged connection")


def package(output, expected_tag=None, check_live=False):
    files = {}
    for name in sorted(set(FILES) | tracked_skills()):
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or invalid release input: {name}")
        files[name] = path.read_bytes()

    portable, codex = (json.loads(files[name]) for name in MANIFESTS)
    version = codex["version"]
    if (not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)
            or any(m.get("version") != version or m.get("name") != "plotpickle-studio"
                   or m.get("apps") for m in (portable, codex))
            or codex.get("mcpServers") != "./.mcp.json" or (ROOT / ".app.json").exists()):
        raise ValueError("Plugin manifests must agree and use the direct Studio MCP connection")
    if expected_tag and expected_tag != f"v{version}":
        raise ValueError(f"Tag {expected_tag} differs from the manifest version {version}")

    servers = json.loads(files[".mcp.json"])["mcpServers"]
    if set(servers) != {"plotpickle-studio"}:
        raise ValueError("Expected exactly one Studio connection")
    endpoint = servers["plotpickle-studio"]
    if set(endpoint) - {"type", "url", "headers", "extensions"} or endpoint.get("headers"):
        raise ValueError("Public Studio connection must not include credentials or overrides")
    auth = endpoint["extensions"]["com.openai"]["auth"]
    if endpoint["type"] != "streamable-http" or auth.get("type") != "oauth" or not auth.get("baseScopes"):
        raise ValueError("Studio MCP must use streamable HTTP and OAuth")
    if check_live:
        check_endpoint(endpoint["url"], auth["baseScopes"])

    portable_mcp = {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
                    "mcpServers": {"plotpickle-studio": {k: v for k, v in endpoint.items() if k != "headers"}}}
    files["mcp.json"] = (json.dumps(portable_mcp, indent=2) + "\n").encode()

    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"PlotPickle-Studio-{version}.zip"
    with ZipFile(archive, "w") as zipped:
        for name, content in sorted(files.items()):
            zipped.writestr(ZipInfo(name), content, compress_type=ZIP_DEFLATED)
    with ZipFile(archive) as zipped:
        if zipped.testzip() or set(zipped.namelist()) != set(files):
            raise ValueError("ZIP verification failed")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--tag")
    parser.add_argument("--check-live", action="store_true")
    args = parser.parse_args()
    print(package(args.output, args.tag, args.check_live))
