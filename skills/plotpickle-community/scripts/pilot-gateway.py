#!/usr/bin/env python3
"""Read-only PlotPickle Community pilot. No network, credentials, invite minting or chat posting."""
import argparse
import json
from pathlib import Path
PILOT = Path(__file__).resolve().parents[1] / "data" / "pilot-community.v1.json"
ROOMS = ("HOME", "CHAT", "ELARA", "SHOW")

def load(path=PILOT):
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    assert cfg["schemaVersion"] == "1.0"
    assert cfg["mode"] == "invitation-only"
    assert tuple(x["name"] for x in cfg["rooms"]) == ROOMS
    assert len({x["id"] for x in cfg["rooms"]}) == 4
    assert not cfg["credentialsStoredByPlotPickle"]
    assert not any((cfg[k] for k in ("inviteRequestsEnabled", "inviteMintingVerified", "browserJoinVerified", "liveMessagingVerified", "elaraAgentVerified")))
    assert all(cfg[k] is None for k in ("browserUrl","relayUrl","inviteUrl"))
    return cfg

def prepare(command):
    cfg = load()
    if command == "preview":
        return {"status":cfg["status"], "community":cfg["name"],"rooms":cfg["rooms"],
                "hostVerified":False,"liveChat":False,"memberCount":"unknown"}
    if command == "request-intent":
        return {"status":"draft-only-not-submitted", "action":"prepare-invitation-request",
                "nextStep":"Authorize a real community backend and hosted browser client before enabling submissions.",
                "recipient":"not-configured", "inviteSent":False, "joinCompleted":False,
                "credentialsRequested":False, "memberVerified":False}
    if command == "acceptance":
        return {"status":"unverified", "checks":cfg["acceptance"],"allPassed":False}
    raise ValueError("Unsupported command")

if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("command",choices=["preview","request-intent","acceptance"])
    try:print(json.dumps(prepare(p.parse_args().command),indent=2,ensure_ascii=False))
    except (AssertionError,KeyError,ValueError,OSError,json.JSONDecodeError) as e:
        print(json.dumps({"status":"fail-closed","error":str(e)}));raise SystemExit(2)
