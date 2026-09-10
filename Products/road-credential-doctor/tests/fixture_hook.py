from __future__ import annotations

import json
import os
import sys
from pathlib import Path


runtime = Path(sys.argv[1])
runtime.mkdir(parents=True, exist_ok=True)
request = json.load(sys.stdin)
phase = str(request["phase"])
consumer = str(request.get("consumer_id") or "")
with (runtime / "events.log").open("a", encoding="utf-8") as handle:
    handle.write(f"{phase}:{consumer}\n")
with (runtime / "requests.jsonl").open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(request, sort_keys=True) + "\n")

if "UNRELATED_SECRET_TOKEN" in os.environ:
    raise SystemExit(10)
fail_phases = (
    set((runtime / "fail_phase").read_text(encoding="utf-8").split())
    if (runtime / "fail_phase").exists()
    else set()
)
if phase in fail_phases:
    raise SystemExit(9)

old_provider_id = str(request.get("old_provider_id") or "")
new_provider_id = str(request.get("new_provider_id") or "")
if phase == "baseline_consumer":
    if (runtime / f"consumer-{consumer}").read_text(encoding="utf-8") != old_provider_id:
        raise SystemExit(8)
elif phase == "create_new":
    new_provider_id = "provider-old" if (runtime / "same_provider_id").exists() else "provider-new"
elif phase == "validate_new":
    if new_provider_id != "provider-new":
        raise SystemExit(8)
elif phase == "update_consumer":
    (runtime / f"consumer-{consumer}").write_text(new_provider_id, encoding="utf-8")
elif phase == "verify_consumer":
    if (runtime / f"consumer-{consumer}").read_text(encoding="utf-8") != new_provider_id:
        raise SystemExit(8)
elif phase == "rollback_consumer":
    (runtime / f"consumer-{consumer}").write_text(old_provider_id, encoding="utf-8")
elif phase == "activate_connector_version":
    (runtime / "active_provider").write_text(new_provider_id, encoding="utf-8")
elif phase == "restore_connector_active_version":
    (runtime / "active_provider").write_text(old_provider_id, encoding="utf-8")
elif phase in {"revoke_old", "retry_revoke_old"}:
    (runtime / "old_revoked").write_text(old_provider_id, encoding="utf-8")
elif phase == "revoke_unused_replacement":
    (runtime / "new_revoked").write_text(new_provider_id, encoding="utf-8")

response = {
    "ok": True,
    "execution_id": f"connector-execution-{phase}-{consumer or 'root'}",
    "authority": "connector",
    "secret_material": False,
}
if phase == "create_new":
    response["provider_id"] = new_provider_id
if (runtime / "malicious_response").exists():
    response["secret"] = "must-be-rejected"
json.dump(response, sys.stdout)
