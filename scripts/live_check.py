#!/usr/bin/env python3
"""Check FestCommand against a running Switch server.

Two modes, standard library only:

  protocol  Deploys a throwaway copy of the template (rooms named
            `livecheck-*`, Switch-only, no messaging app) with three
            stand-in agents, then acts as each agent over the real agent
            protocol (event stream + heartbeat + operations) and checks the
            platform behaviour FestCommand relies on: who can write which
            document, who can enter which room, links, hand-offs, kickoffs.
            Deletes everything it created afterwards (--keep to leave it).
            No coding agent or provider login is needed.

  inspect   Reads a real deployment (`--fest techstorm` by default) and
            checks that the agents' kickoffs produced their live documents:
            each one created by the right agent, valid, and equal to the
            template's baseline until something is approved.

Which server:
  --console                 the server Switch Console runs on this computer
                            (reads its port and admin login from the Console)
  --url URL --email E       any server; the password comes from
                            SWITCH_ADMIN_PASSWORD

Examples:
  python scripts/live_check.py protocol --console
  python scripts/live_check.py inspect --console
  SWITCH_ADMIN_PASSWORD=... python scripts/live_check.py protocol \
      --url http://localhost:8000 --email admin@switch.local
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "festcommand.template.yaml"
SLOTS = ("concierge", "bracket_marshal", "sponsor_tracker")
ROLE = {"concierge": "concierge", "bracket_marshal": "bracket-marshal", "sponsor_tracker": "sponsor-tracker"}

results: list[bool] = []


def check(ok: object, what: str, detail: object = "") -> bool:
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {what}")
    if detail and not ok or (detail and isinstance(detail, str) and detail.startswith("HTTP")):
        print(f"        {str(detail)[:220]}")
    return bool(ok)


# ── server access ─────────────────────────────────────────────────────────────

def console_server() -> tuple[str, str, str]:
    """URL and admin login of the server Switch Console runs locally."""
    base = Path(os.environ.get("APPDATA") or Path.home() / ".config")
    candidates = [base / "switchdash/local-switch-server/native/run/switch-core.env",
                  Path.home() / "Library/Application Support/switchdash/local-switch-server/native/run/switch-core.env"]
    for path in candidates:
        if path.exists():
            env = dict(line.split("=", 1) for line in path.read_text().splitlines() if "=" in line)
            return (f"http://127.0.0.1:{env['SERVER_PORT']}", env["GATEWAY_ADMIN_EMAIL"],
                    env["GATEWAY_ADMIN_PASSWORD"])
    sys.exit("No local Switch Console server found. Start it in Switch Console, or pass --url.")


class Admin:
    """The gateway API, signed in as an admin (cookie session)."""

    def __init__(self, url: str, email: str, password: str):
        self.url = url.rstrip("/")
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        status, body = self.call("POST", "/gateway/auth/login", {"email": email, "password": password})
        if status != 200:
            sys.exit(f"Login to {self.url} failed: HTTP {status} {body}")

    def call(self, method: str, path: str, body: object = None) -> tuple[int, object]:
        req = urllib.request.Request(self.url + path, method=method,
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with self.opener.open(req, timeout=300) as r:
                raw = r.read()
                return r.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except ValueError:
                return e.code, raw.decode(errors="replace")

    def room_docs(self, room_id: str) -> dict[str, dict]:
        """Every document in a room, with content, by name."""
        _, docs = self.call("GET", f"/gateway/rooms/{room_id}/documents")
        out = {}
        for d in docs if isinstance(docs, list) else []:
            _, full = self.call("GET", f"/gateway/rooms/{room_id}/documents/{d['id']}")
            out[d["name"]] = {**d, "content": (full or {}).get("content", "")}
        return out


class Agent:
    """One agent connected over the real protocol: an SSE event stream, a
    heartbeat every 2 s, and operations sent with its connection id."""

    def __init__(self, url: str, name: str, agent_id: str, api_key: str):
        self.url, self.name, self.id, self.key = url, name, agent_id, api_key
        self.conn = str(uuid.uuid4())
        self.events: list[dict] = []
        self.generation = None
        self.ready = threading.Event()
        threading.Thread(target=self._stream, daemon=True).start()
        if not self.ready.wait(30):
            sys.exit(f"{name}: the event stream never opened")
        threading.Thread(target=self._beat, daemon=True).start()

    def _request(self, method: str, path: str, body: object = None, headers: dict | None = None):
        return urllib.request.Request(self.url + path, method=method,
                                      data=None if body is None else json.dumps(body).encode(),
                                      headers={"Authorization": f"Bearer {self.key}",
                                               "Content-Type": "application/json", **(headers or {})})

    def _stream(self) -> None:
        query = (f"connection_id={self.conn}&scope=single&filter=all"
                 "&client=festcommand-live-check&client_version=1.0.0")
        req = self._request("GET", f"/agents/{self.id}/events?{query}", headers={"Accept": "text/event-stream"})
        with urllib.request.urlopen(req, timeout=3600) as r:
            data: list[str] = []
            for raw in r:
                line = raw.decode("utf-8").rstrip("\r\n")
                if line.startswith("data:"):
                    data.append(line[5:].lstrip())
                elif not line and data:
                    try:
                        event = json.loads("\n".join(data))
                    except ValueError:
                        event = {"raw": "\n".join(data)}
                    data = []
                    self.events.append(event)
                    if event.get("type") == "connection_state" or "connection_id" in event:
                        self.generation = event.get("generation")
                        self.ready.set()

    def _beat(self) -> None:
        while True:
            try:
                body = {"connection_id": self.conn, "generation": self.generation}
                urllib.request.urlopen(self._request("POST", f"/agents/{self.id}/connection/beat", body),
                                       timeout=10).read()
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(2)

    def op(self, _operation: str, **args) -> tuple[int, object]:
        req = self._request("POST", f"/agents/{self.id}/ops/{_operation}", args,
                            {"X-Switch-Connection-Id": self.conn})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read())["result"]
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            try:
                text = json.loads(text).get("detail", text)
            except ValueError:
                pass
            return e.code, text

    def read(self, doc_id: str) -> str:
        """A document's content, through load_internal_documents."""
        status, r = self.op("load_internal_documents", ids=[doc_id])
        if status != 200:
            return ""
        items = r if isinstance(r, list) else r.get("documents", list(r.values()))
        return items[0].get("content", "") if items else ""


def docs_of(payload: object) -> dict[str, dict]:
    return {d["name"]: d for d in (payload or {}).get("documents", [])} if isinstance(payload, dict) else {}


def created_id(result: object) -> str | None:
    return (result.get("id") or result.get("document_id")) if isinstance(result, dict) else None


# ── protocol mode ─────────────────────────────────────────────────────────────

def protocol(admin: Admin, fest: str, keep: bool) -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    # Stand-in agents fill the slots, so each slot has to accept an existing agent.
    text = text.replace("    type: agent\n", "    type: agent\n    allow_existing: true\n")
    # No messaging app: the rooms stay Switch-only instead of opening channels.
    text = text.replace("    default: [$first]\n    required: false\n", "    required: false\n", 1)

    names = {slot: f"{fest}-{ROLE[slot]}" for slot in SLOTS}
    agents: dict[str, dict] = {}
    print(f"── deploy: throwaway copy as '{fest}', three stand-in agents, no messaging app")
    for slot, name in names.items():
        status, r = admin.call("POST", "/gateway/agents/register",
                               {"agent_type": "claude-code", "name": name, "overwrite": True,
                                "description": f"FestCommand live check stand-in ({slot})"})
        if not check(status == 200, f"register stand-in {name}", r):
            sys.exit(1)
        agents[slot] = r
    status, run = admin.call("POST", "/gateway/rooms/from-template-document",
                             {"template": text, "template_name": "FestCommand live check",
                              "inputs": {"fest": fest, "title": "Live Check"}, "filled": names})
    room_info = (run or {}).get("room") or {} if isinstance(run, dict) else {}
    check(status == 201 and not room_info.get("errors"), "template deploys (3 rooms, documents, group, links)", run)
    if status != 201:
        sys.exit(1)
    rooms = {r["room_name"].removeprefix(f"{fest}-"): r["room_id"] for r in room_info["rooms"]}

    try:
        run_agent_checks(admin, rooms, names, agents)
    finally:
        if keep:
            print(f"\n(--keep: left the '{fest}' rooms and agents in place)")
        else:
            for room_id in rooms.values():
                admin.call("DELETE", f"/gateway/rooms/{room_id}")
            if room_info.get("group_id"):
                admin.call("DELETE", f"/gateway/room-groups/{room_info['group_id']}")
            for a in agents.values():
                admin.call("DELETE", f"/gateway/agents/{a['id']}")
            print(f"\n(cleaned up the '{fest}' rooms, group and stand-in agents)")


def run_agent_checks(admin: Admin, rooms: dict, names: dict, agents: dict) -> None:
    url = admin.url
    print("\n── connect: three agents over the real protocol (event stream + heartbeat)")
    concierge, marshal, tracker = (Agent(url, names[s], agents[s]["id"], agents[s]["api_key"]) for s in SLOTS)
    check(True, "all three agents hold a live connection")

    print("\n── bracket-marshal in tournament-ops")
    status, ops = marshal.op("connect_to_room", room_id=rooms["tournament-ops"])
    check(status == 200, "connect_to_room(tournament-ops)", ops)
    ops_docs = docs_of(ops)
    check({"bracket_state.json", "schedule_and_rules.md"} <= set(ops_docs),
          "ops holds bracket_state.json and schedule_and_rules.md", sorted(ops_docs))
    status, ctx = marshal.op("read_context", room_id=rooms["tournament-ops"])
    check(status == 200 and "bracket_live_" in json.dumps(ctx), "the room's kickoff names the live documents")

    baseline = ops_docs.get("bracket_state.json", {})
    status, r = marshal.op("update_room_document", document_id=baseline.get("id", "-"), content="{}")
    check(status == 403, "cannot update the template's bracket_state.json (only a document's creator can)",
          f"HTTP {status}: {r}")

    bracket = json.loads(marshal.read(baseline.get("id", "-")) or "{}")
    check(bracket.get("tournaments"), "reads bracket_state.json")
    live: dict[str, str | None] = {}
    for game, t in bracket.get("tournaments", {}).items():
        content = json.dumps({"event": bracket["event"], "tournament": game,
                              "last_updated": bracket["last_updated"], **t}, indent=1, ensure_ascii=False)
        status, r = marshal.op("create_room_document", name=f"bracket_live_{game}.json",
                               description=f"Live {game} bracket", content=content,
                               instructions="Written only by the bracket marshal.")
        live[game] = created_id(r) if status == 200 else None
        check(status == 200, f"creates bracket_live_{game}.json ({len(content.encode()) // 1024} KB)", r)
    status, r = marshal.op("create_room_document", name="approvals_live.json", description="Approval queue",
                           instructions="Written only by the bracket marshal.",
                           content=json.dumps({"pending_approvals": [], "audit_log": []}))
    check(status == 200, "creates approvals_live.json last", r)

    first = next(iter(live.values()), None)
    if first:
        doc = json.loads(marshal.read(first))
        doc["live_check"] = "approved result recorded"
        status, r = marshal.op("update_room_document", document_id=first, content=json.dumps(doc))
        check(status == 200, "updates its own live document (an approved result)", r)
    status, r = marshal.op("connect_to_room", room_id=rooms["sponsor-finance"])
    check(status >= 400, "cannot enter sponsor-finance", f"HTTP {status}: {r}")

    print("\n── concierge: helpdesk, then across the link into ops")
    status, hd = concierge.op("connect_to_room", room_id=rooms["public-helpdesk"])
    check(status == 200, "connect_to_room(public-helpdesk)", hd)
    check("schedule_and_rules.md" in docs_of(hd), "helpdesk holds schedule_and_rules.md")
    status, r = concierge.op("create_room_document", name="announcements.md", content="# Announcements\n",
                             description="Approved announcements", instructions="Concierge appends here.")
    check(status == 200, "creates announcements.md", r)
    status, links = concierge.op("list_linked_rooms")
    check(status == 200 and rooms["tournament-ops"] in json.dumps(links), "list_linked_rooms shows the link to ops")
    status, r = concierge.op("connect_to_room", room_id=rooms["tournament-ops"])
    check(status == 200, "connects to tournament-ops (a member of both rooms)", r)
    check(any(n.startswith("bracket_live_") for n in docs_of(r)), "sees the marshal's live documents")
    if first:
        check("approved result recorded" in concierge.read(first), "reads the marshal's latest result")
        status, r = concierge.op("update_room_document", document_id=first, content="{}")
        check(status == 403, "cannot overwrite the marshal's document", f"HTTP {status}: {r}")
    seen = len(marshal.events)
    status, r = concierge.op("send_targeted_message", target_names=[marshal.name],
                             body="⚔️ DISPUTE REPORT (live check): MATCH-47, disconnect at 1-1, 85'.")
    check(status == 200, "hands a dispute to the marshal (send_targeted_message)", r)
    deadline = time.time() + 15
    while time.time() < deadline and not any("DISPUTE REPORT (live check)" in json.dumps(e, ensure_ascii=False)
                                             for e in marshal.events[seen:]):
        time.sleep(0.5)
    check(any("DISPUTE REPORT (live check)" in json.dumps(e, ensure_ascii=False) for e in marshal.events[seen:]),
          "the marshal receives it on its event stream, addressed to it")
    status, r = concierge.op("connect_to_room", room_id=rooms["sponsor-finance"])
    check(status >= 400, "cannot enter sponsor-finance", f"HTTP {status}: {r}")

    print("\n── sponsor-tracker in sponsor-finance")
    status, fin = tracker.op("connect_to_room", room_id=rooms["sponsor-finance"])
    check(status == 200, "connect_to_room(sponsor-finance)", fin)
    ledger = docs_of(fin).get("sponsor_ledger.json", {})
    status, r = tracker.op("update_room_document", document_id=ledger.get("id", "-"), content="{}")
    check(status == 403, "cannot update the template's sponsor_ledger.json", f"HTTP {status}: {r}")
    body = tracker.read(ledger.get("id", "-"))
    check("VENDOR-03" in body, "the ledger's approval queue holds VENDOR-03")
    status, r = tracker.op("create_room_document", name="ledger_live.json", content=body,
                           description="Live ledger", instructions="Written only by the sponsor tracker.")
    check(status == 200, f"creates ledger_live.json ({len(body.encode()) // 1024} KB)", r)
    status, r = tracker.op("connect_to_room", room_id=rooms["tournament-ops"])
    check(status == 200, "connects to tournament-ops (hears TOURNAMENT COMPLETE there)", r)


# ── inspect mode ──────────────────────────────────────────────────────────────

def inspect(admin: Admin, fest: str) -> None:
    status, listing = admin.call("GET", "/gateway/rooms")
    rooms = {r["name"].removeprefix(f"{fest}-"): r for r in listing if r["name"].startswith(f"{fest}-")} \
        if isinstance(listing, list) else {}
    if not check(len(rooms) == 3, f"three '{fest}-*' rooms exist", sorted(rooms)):
        sys.exit(1)
    for name, r in sorted(rooms.items()):
        where = r.get("bridge_display_name") and f"{r['bridge_type']} '{r['bridge_display_name']}'"
        print(f"        {name:16} {r['agent_count']} agents, {where or 'Switch-only'}")
    _, agent_list = admin.call("GET", "/gateway/agents")
    by_id = {a["id"]: a["name"] for a in agent_list} if isinstance(agent_list, list) else {}

    def owned(docs: dict, name: str, role: str) -> dict | None:
        d = docs.get(name)
        who = by_id.get(d.get("created_by_agent_id")) if d else None
        check(d and who == f"{fest}-{role}", f"{name} created by {fest}-{role}", f"found: {who or 'missing'}")
        return d

    print("\n── live documents the kickoffs create")
    ops = admin.room_docs(rooms["tournament-ops"]["id"])
    base = json.loads(ops["bracket_state.json"]["content"])
    for game, t in base["tournaments"].items():
        d = owned(ops, f"bracket_live_{game}.json", "bracket-marshal")
        if d:
            doc = json.loads(d["content"])
            changed = [k for k, v in t.items() if doc.get(k) != v]
            check(doc.get("tournament") == game, f"  valid, tournament={game}"
                  + (f" (changed since kickoff: {', '.join(changed)})" if changed else ", equal to the baseline"))
    owned(ops, "approvals_live.json", "bracket-marshal")
    fin = admin.room_docs(rooms["sponsor-finance"]["id"])
    d = owned(fin, "ledger_live.json", "sponsor-tracker")
    if d:
        check(json.loads(d["content"]).get("pending_approvals") is not None, "  valid, approval queue present")
    owned(admin.room_docs(rooms["public-helpdesk"]["id"]), "announcements.md", "concierge")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("mode", choices=["protocol", "inspect"])
    p.add_argument("--console", action="store_true", help="use the server Switch Console runs on this computer")
    p.add_argument("--url", help="Switch API URL, e.g. http://localhost:8000")
    p.add_argument("--email", help="admin email (password from SWITCH_ADMIN_PASSWORD)")
    p.add_argument("--fest", help="fest short name (protocol: livecheck, inspect: techstorm)")
    p.add_argument("--keep", action="store_true", help="protocol: leave the throwaway deployment in place")
    a = p.parse_args()

    if a.console:
        url, email, password = console_server()
    elif a.url and a.email and os.environ.get("SWITCH_ADMIN_PASSWORD"):
        url, email, password = a.url, a.email, os.environ["SWITCH_ADMIN_PASSWORD"]
    else:
        p.error("pass --console, or --url and --email with SWITCH_ADMIN_PASSWORD set")
    admin = Admin(url, email, password)
    print(f"Switch server: {admin.url}\n")
    if a.mode == "protocol":
        protocol(admin, a.fest or "livecheck", a.keep)
    else:
        inspect(admin, a.fest or "techstorm")
    print(f"\nRESULT: {sum(results)}/{len(results)} checks passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
