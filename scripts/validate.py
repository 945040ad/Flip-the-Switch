#!/usr/bin/env python3
"""
FestCommand consistency checker.

Agents answer from the room documents, so a contradiction between documents
turns into a confidently wrong answer in chat. This script checks that:

  * the template was built from the current sources, and passes the rules
    the Switch server applies (mirrored from sandbox-quantum/switch core:
    param specs, the fields each resource type reads, `if:` conditions,
    agent-name and display-name limits, at most one group);
  * every placeholder is a param, a `{key.name}` or a Switch built-in, and
    no embedded document contains one (Switch has no brace escape);
  * agents mention only agents they share a room with, and each live
    document created at kickoff copies a baseline from its own room without
    colliding with a provisioned name;
  * every match in the published schedule exists in bracket_state.json at the
    same time and stage, and vice versa;
  * bracket progression is consistent (winners flow into the next match,
    scores are legal, nothing after the snapshot time is already completed);
  * the ledger's arithmetic adds up, the budget is not over-allocated, prize
    amounts match the rulebook's prize table, and booth numbers match the venue
    map;
  * every approval code is a 4-character hex code.

Usage:  python scripts/validate.py          (exit code 1 on any error)
Standard library only; template checks use PyYAML when it is installed.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "documents"

errors: list[str] = []
passes = 0


def check(cond: bool, msg: str) -> bool:
    global passes
    if cond:
        passes += 1
    else:
        errors.append(msg)
    return cond


def section(title: str) -> None:
    print(f"\n── {title}")


def done(title: str, before: int) -> None:
    new = errors[before:]
    if new:
        for e in new:
            print(f"  ✗ {e}")
    else:
        print(f"  ✓ {title}")


# ─────────────────────────────── loading ────────────────────────────────

def load():
    bracket = json.loads((DOCS / "bracket_state.json").read_text(encoding="utf-8"))
    ledger = json.loads((DOCS / "sponsor_ledger.json").read_text(encoding="utf-8"))
    schedule = (DOCS / "schedule_and_rules.md").read_text(encoding="utf-8")
    return bracket, ledger, schedule


def all_matches(bracket: dict) -> dict[str, dict]:
    """Flatten every match-like object (anything with a match_id) with its game."""
    found: dict[str, dict] = {}

    def walk(obj, game):
        if isinstance(obj, dict):
            if "match_id" in obj and ("scheduled_time" in obj or "status" in obj):
                found.setdefault(obj["match_id"], {**obj, "_game": game})
            for v in obj.values():
                walk(v, game)
        elif isinstance(obj, list):
            for v in obj:
                walk(v, game)

    for game, t in bracket["tournaments"].items():
        walk(t, game)
    return found


# ─────────────────────────────── schedule ───────────────────────────────

DAY_DATES = {"1": "2026-12-14", "2": "2026-12-15"}


def schedule_slots(schedule: str) -> dict[str, tuple[str, str]]:
    """MATCH-ID -> (ISO local time 'YYYY-MM-DDTHH:MM', stage) from the day tables."""
    slots: dict[str, tuple[str, str]] = {}
    for day, body in re.findall(r"## Day (\d) Schedule.*?\n(.*?)(?=\n---|\n## )", schedule, re.S):
        lines = [l for l in body.splitlines() if l.startswith("|")]
        header = [c.strip() for c in lines[0].strip("|").split("|")]
        for row in lines[2:]:
            cells = [c.strip() for c in row.strip("|").split("|")]
            t = re.sub(r"\*", "", cells[0])
            for col, cell in zip(header[1:], cells[1:]):
                ids = re.findall(r"MATCH-(\d+)", cell)
                rng = re.search(r"MATCH-(\d+) to MATCH-(\d+)", cell)
                if rng:
                    ids = [f"{i:02d}" for i in range(int(rng[1]), int(rng[2]) + 1)]
                for i in ids:
                    slots[f"MATCH-{i}"] = (f"{DAY_DATES[day]}T{t}", col)
    return slots


def check_schedule_vs_bracket(bracket, schedule):
    b0 = len(errors)
    matches = all_matches(bracket)
    slots = schedule_slots(schedule)
    for mid, (when, stage) in sorted(slots.items()):
        if not check(mid in matches, f"schedule lists {mid} but bracket_state.json has no such match"):
            continue
        m = matches[mid]
        bt = m.get("scheduled_time", "")[:16]
        check(bt == when, f"{mid}: schedule says {when}, bracket says {bt}")
        if "stage" in m:
            check(m["stage"] == stage, f"{mid}: schedule says {stage}, bracket says {m['stage']}")
    for mid, m in matches.items():
        check(mid in slots, f"{mid} ({m['_game']}) is in the bracket but not in the published schedule")
    done(f"{len(slots)} scheduled matches agree with bracket_state.json (time + stage)", b0)


# ─────────────────────────────── bracket ────────────────────────────────

HEX = re.compile(r"^#[0-9a-f]{4}$")


def legal_valorant_map(a: int, b: int) -> bool:
    hi, lo = max(a, b), min(a, b)
    return (hi == 13 and lo <= 11) or (hi >= 14 and hi - lo == 2)


def check_bracket(bracket):
    b0 = len(errors)
    snap = datetime.fromisoformat(bracket["last_updated"])
    matches = all_matches(bracket)
    winners = {mid: m.get("winner") for mid, m in matches.items()}
    # The marshal splits the bracket into bracket_live_<game>.json by these keys.
    skill = (ROOT / "agents" / "bracket-marshal" / "SKILL.md").read_text(encoding="utf-8")
    games = re.search(r"one per key of `tournaments`\s*\(([^)]*)\)", skill)
    listed = set(re.findall(r"`([a-z0-9_]+)`", games.group(1))) if games else set()
    check(listed == set(bracket["tournaments"]),
          f"bracket-marshal SKILL.md lists games {sorted(listed)}, bracket_state.json has {sorted(bracket['tournaments'])}")

    for mid, m in matches.items():
        when = m.get("scheduled_time")
        if when and m.get("status") == "completed":
            check(datetime.fromisoformat(when) <= snap,
                  f"{mid} is 'completed' but scheduled after the snapshot ({when} > {bracket['last_updated']})")
        if when and m.get("status") == "pending":
            overdue = (snap - datetime.fromisoformat(when)).total_seconds() / 3600
            check(overdue < 2, f"{mid} is still 'pending' {overdue:.1f}h after its slot. Mark it "
                               "in_progress / awaiting_result, or record the result")
        if m.get("status") == "completed" and "winner" in m:
            check(bool(m.get("winner")), f"{mid} is completed but has no winner")
        if "approval_hash" in m:
            check(bool(HEX.match(m["approval_hash"])), f"{mid}: approval code {m['approval_hash']!r} is not 4 hex chars")

        # Progression: "Winner of MATCH-X vs Winner of MATCH-Y" fills team_a/team_b (or player_a/b).
        notes = m.get("notes") or ""
        refs = re.findall(r"(Winner|Loser) of (?:[A-Z ]+\()?(MATCH-\d+)", notes)
        if len(refs) == 2:
            for side, (kind, src) in zip(("a", "b"), refs):
                if kind != "Winner" or src not in matches:
                    continue
                field = f"team_{side}" if f"team_{side}" in m else f"player_{side}"
                expected = winners.get(src)
                actual = m.get(field)
                check(actual == expected,
                      f"{mid}.{field} is {actual!r} but {src} winner is {expected!r}")

    # Valorant series scores
    val = bracket["tournaments"]["valorant"]
    for m in val["matches"]:
        sc = m.get("score")
        if not sc:
            continue
        need = 3 if m["round"] == "grand_final" else 2
        wins_a = sum(1 for mp in sc["maps"] if mp["winner"] == m["team_a"])
        wins_b = sum(1 for mp in sc["maps"] if mp["winner"] == m["team_b"])
        check((wins_a, wins_b) == (sc["team_a_maps"], sc["team_b_maps"]), f"{m['match_id']}: map tally mismatch")
        check(max(wins_a, wins_b) == need, f"{m['match_id']}: winner needs {need} maps")
        check(m["winner"] == (m["team_a"] if wins_a > wins_b else m["team_b"]), f"{m['match_id']}: winner mismatch")
        for mp in sc["maps"]:
            check(legal_valorant_map(mp["score_a"], mp["score_b"]),
                  f"{m['match_id']}: {mp['map']} {mp['score_a']}-{mp['score_b']} is not a legal Valorant map score")

    # BGMI points arithmetic
    bg = bracket["tournaments"]["bgmi"]
    pts = bg["points_system"]

    def placement_points(p: int) -> int:
        for k, v in pts["placement"].items():
            lo, _, hi = k.partition("-")
            if int(lo) <= p <= int(hi or lo):
                return v
        return 0

    squads = {s["name"] for s in bg["squads"]}
    for rnd in bg["rounds"]:
        for lobby in rnd["lobbies"]:
            for r in lobby.get("results") or []:
                check(r["squad"] in squads, f"BGMI {lobby['match_id']}: unknown squad {r['squad']}")
                check(r["placement_points"] == placement_points(r["placement"]),
                      f"BGMI {lobby['match_id']}: {r['squad']} placement points wrong")
                check(r["kill_points"] == r["kills"] * pts["per_kill"], f"BGMI {lobby['match_id']}: kill points wrong")
                check(r["total"] == r["placement_points"] + r["kill_points"], f"BGMI {lobby['match_id']}: total wrong")

    check_approval_lists(bracket, "bracket_state.json")
    done(f"{len(matches)} matches: progression, scores, statuses and approval codes are consistent", b0)


# ─────────────────────────────── ledger ─────────────────────────────────

ORDINAL = {"first": "🥇 1st Place", "second": "🥈 2nd Place", "third": "🥉 3rd Place"}
GAME_ROWS = {"valorant": "Valorant 5v5", "bgmi": "BGMI 4-Squad", "fifa25": "FIFA 25 1v1",
             "rocket_league": "Rocket League 3v3", "hackathon": "Hackathon"}
COSPLAY_ROWS = {"best_overall": "Best Overall", "best_gaming_character": "Best Gaming Character",
                "best_craftsmanship": "Best Craftsmanship", "best_group": "Best Group",
                "audience_choice": "Audience Choice"}
EXTRA = {("bgmi", "mvp"): "BGMI MVP", ("hackathon", "peoples_choice"): "Hackathon People's Choice"}


def inr(text: str) -> int:
    return int(re.sub(r"[^\d]", "", text))


def check_approval_lists(doc: dict, name: str) -> None:
    """Both approval protocols keep pending_approvals and audit_log lists."""
    for key in ("pending_approvals", "audit_log"):
        check(isinstance(doc.get(key), list), f"{name} needs a '{key}' list for the approval protocol")
    for p in doc.get("pending_approvals") or []:
        check(bool(HEX.match(p.get("code", ""))), f"{name}: pending approval {p.get('id')} has a bad code")


def check_ledger(ledger, schedule):
    b0 = len(errors)
    check_approval_lists(ledger, "sponsor_ledger.json")
    sponsorship = sum(s["commitment_inr"] for s in ledger["sponsors"])
    inc = ledger.get("income", {})
    check(inc.get("sponsorship") == sponsorship, "income.sponsorship != sum of sponsor commitments")
    check(ledger["total_budget"] == sum(v for v in inc.values() if isinstance(v, int)),
          "total_budget != sum of income lines")

    cats = ledger["expenses"]["categories"]
    alloc = spent = 0
    for name, c in cats.items():
        paid = sum(i["amount"] for i in c.get("items", []) if i["status"] == "paid")
        check(c["spent"] == paid, f"expenses.{name}.spent is {c['spent']} but paid items sum to {paid}")
        pct = round(100 * c["spent"] / c["allocated"], 1)
        check(abs(c["utilization_pct"] - pct) < 0.05, f"expenses.{name}.utilization_pct should be {pct}")
        if pct > 80:
            check(any(name in a["message"] and not a["resolved"] for a in ledger["alerts"]),
                  f"expenses.{name} is at {pct}% but has no open budget alert")
        alloc += c["allocated"]
        spent += c["spent"]
    s = ledger["expenses"]["summary"]
    check(s["total_allocated"] == alloc and s["total_spent"] == spent and s["remaining"] == alloc - spent,
          "expenses.summary does not match the categories")

    pp = ledger["prize_pool"]
    for g, t in pp["tournaments"].items():
        check(t["total"] == sum(p["amount"] for p in t["prizes"].values()), f"prize_pool.{g}.total is wrong")
    check(pp["total_allocated"] == sum(t["total"] for t in pp["tournaments"].values()), "prize_pool.total_allocated is wrong")
    check(alloc + pp["total_allocated"] <= ledger["total_budget"],
          f"over-allocated: expenses {alloc} + prizes {pp['total_allocated']} > budget {ledger['total_budget']}")
    check(ledger["total_spent"] == spent + pp["total_disbursed"], "total_spent != expenses spent + prizes disbursed")
    check(abs(ledger["budget_utilization_pct"] - round(100 * ledger["total_spent"] / ledger["total_budget"], 1)) < 0.05,
          "budget_utilization_pct is wrong")

    # Prize table in the rulebook
    tbl = re.search(r"\| Tournament \|.*?\n\|[-| ]+\n(.*?)\n\n", schedule, re.S)
    rows = {r.split("|")[1].strip(): [inr(c) for c in r.split("|")[2:5]] for r in tbl[1].splitlines()}
    tours = pp["tournaments"]

    def amount(game: str, key: str):
        return ((tours.get(game) or {}).get("prizes", {}).get(key) or {}).get("amount")

    for g, label in GAME_ROWS.items():
        want = [amount(g, k) for k in ("first", "second", "third")]
        check(rows.get(label) == want, f"prizes for {label}: rulebook {rows.get(label)} vs ledger {want}")
    for key, label in COSPLAY_ROWS.items():
        m = re.search(rf"\| {re.escape(label)} \| ₹([\d,]+)", schedule)
        check(bool(m) and inr(m[1]) == amount("cosplay", key),
              f"cosplay '{label}' prize differs between rulebook and ledger")
    for (g, key), label in EXTRA.items():
        m = re.search(rf"\*\*{re.escape(label)}\*\*.*?₹([\d,]+)", schedule)
        check(bool(m) and inr(m[1]) == amount(g, key),
              f"'{label}' prize differs between rulebook and ledger")
    m = re.search(r"Total Prize Pool: ₹([\d,]+)", schedule)
    check(bool(m) and inr(m[1]) == pp["total_allocated"], "rulebook 'Total Prize Pool' != ledger prize_pool.total_allocated")

    # Booths
    for s_ in ledger["sponsors"]:
        booth = (s_["deliverables"] or {}).get("booth")
        m = re.search(rf"\| \*\*(B\d)\*\* \| {re.escape(s_['name'])} \|", schedule)
        if booth and m:
            check(booth["location"].startswith(m[1]), f"{s_['name']}: ledger booth {booth['location']!r} vs rulebook {m[1]}")
        check(bool(m) == bool(booth), f"{s_['name']}: booth present in only one of ledger / rulebook")

    for v in ledger["vendor_payments"]:
        if "approval_hash" in v:
            check(bool(HEX.match(v["approval_hash"])), f"{v['id']}: approval code is not 4 hex chars")
    lakh = re.sub(r"(\d)(?=(\d\d)+\d{3}$)", r"\1,", str(ledger["total_budget"]))
    lakh = lakh[:-3] + "," + lakh[-3:] if len(lakh) > 3 else lakh
    done(f"ledger arithmetic, budget, prize table and booths agree (budget ₹{lakh})", b0)


# ─────────────────────────────── template ───────────────────────────────

ADDRESSING = {"owner", "owner-agents", "anyone"}
AGENT_REQUIRED = ("provider", "directory", "instructions")
# Built-ins documented in Switch docs/TEMPLATES.md ($first is only valid in default chains).
BUILTINS = {"creator", "creator_email", "agents_dir", "date", "timestamp", "first"}
PLACEHOLDER = re.compile(r"\{\$?[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_]+)?\}")

# Mirrors of the server's own schema (sandbox-quantum/switch, core/switch_core):
# rooms_yaml.ParamSpec / RoomSpec / GroupMeta and the fields that
# agent_templates' planner and template_v2.compile_v2 read. Keeping them here
# lets CI catch a template the server would refuse, without a Switch server.
PARAM_KEYS = {"type", "description", "label", "default", "required", "input", "enum",
              "multiline", "pattern", "min", "max", "if"}
PARAM_TYPES = {"string", "number", "boolean", "enum", "agent", "bridge", "room", "user",
               "provider", "location", "machine", "directory"}
CHAIN_TYPES = {"agent", "bridge", "room", "provider", "location", "machine"}
OPTIONAL_WITHOUT_DEFAULT = {"string", "bridge", "room"}
AGENT_KEYS = {"type", "if", "name", "display_name", "description", "icon_url", "instructions",
              "provider", "machine", "location", "directory", "model", "addressing", "isolation",
              "auto_mode", "auto_approve", "allow_existing", "can_manage_agents", "connections",
              "advanced_config", "repo", "sources", "join"}
ROOM_KEYS = {"type", "if", "kickoff", "group", "name", "description", "instructions", "bridge",
             "channel_type", "read_visibility", "write_visibility", "agents", "users", "roles",
             "references", "packages", "docs", "aliases"}
GROUP_KEYS = {"type", "if", "name", "description", "color", "links"}
AGENT_NAME = re.compile(r"\A[a-z0-9][a-z0-9._-]*\Z")
# Agent operations (MCP tools) the server defines, from
# core/switch_core/bridges/agent/operations/definitions.py. Instructions that
# name a tool not on this list would send an agent after something that
# doesn't exist.
SWITCH_OPERATIONS = {
    "list_rooms", "connect_to_room", "list_references", "list_linked_rooms",
    "load_internal_documents", "create_room_document", "update_room_document",
    "delete_room_document", "read_context", "list_participants", "post_message",
    "send_targeted_message", "create_room", "list_roles", "get_role_detail",
    "define_role", "edit_role", "delete_role", "assume_role", "release_role",
    "list_reference_types", "create_reference", "attach_reference_to_room",
    "list_all_references", "link_rooms", "unlink_rooms", "list_bridges",
    "invite_agent_to_room", "remove_agent_from_room", "add_users_to_room",
    "list_all_rooms", "list_room_groups", "create_room_group",
    "get_room_group_detail", "create_room_from_yaml", "get_template_guide",
    "list_templates", "get_template", "run_template", "save_template",
    "update_template", "delete_template", "list_agents", "get_agent_detail",
    "request_agent_deletion", "update_agent_detail", "get_room_detail",
    "update_room", "archive_room", "unarchive_room",
}
OPERATION_LIKE = re.compile(
    r"\b((?:list|connect|load|create|update|delete|send|post|get|run|save|invite|"
    r"remove|add|link|unlink|assume|release|define|edit|archive|unarchive|attach|request)"
    r"_[a-z_]+)\b")
CONDITION = re.compile(r"^\{([A-Za-z_][A-Za-z0-9_]*)\}(?:\s*(==|!=)\s*(.+))?$")


def conditional_values(node):
    """Yield each `if:` condition written in a `[{if, value}, ...]` field."""
    if isinstance(node, list) and node and all(isinstance(i, dict) and "value" in i for i in node):
        for item in node:
            if "if" in item:
                yield item["if"]
            yield from conditional_values(item["value"])
    elif isinstance(node, dict):
        for v in node.values():
            yield from conditional_values(v)
    elif isinstance(node, list):
        for v in node:
            yield from conditional_values(v)


def check_switch_schema(t: dict) -> None:
    """The rules the Switch server applies on upload and when planning a run."""
    params = t.get("params") or {}
    for name, spec in params.items():
        check(isinstance(spec, dict) and set(spec) <= PARAM_KEYS,
              f"param {name}: unknown key(s) {sorted(set(spec) - PARAM_KEYS)}")
        ptype = spec.get("type", "string")
        check(ptype in PARAM_TYPES, f"param {name}: unknown type {ptype!r}")
        check(spec.get("input", "ask") in {"ask", "advanced", "fixed"}, f"param {name}: bad input")
        default = spec.get("default")
        if isinstance(default, list):
            check(ptype in CHAIN_TYPES and bool(default), f"param {name}: a list default needs a chain type")
        check(not (spec.get("input") == "fixed" and default is None), f"param {name}: fixed needs a default")
        check(not (spec.get("required") is False and default is None and ptype not in OPTIONAL_WITHOUT_DEFAULT),
              f"param {name}: a {ptype} param without a default cannot be optional")
        check(not ({"min", "max"} & set(spec)) or ptype == "number", f"param {name}: min/max apply to number params")
        check(ptype != "enum" or bool(spec.get("enum")), f"param {name}: an enum param needs enum: [values]")
        if "pattern" in spec:
            check(ptype == "string", f"param {name}: pattern applies to string params")
            try:
                re.compile(spec["pattern"])
            except re.error:
                check(False, f"param {name}: pattern is not a valid regex")
    # Agent names must match the server's VALID_AGENT_NAME_RE and display
    # names fit MAX_DISPLAY_NAME_LENGTH, with defaults and with the longest
    # value each string param's pattern admits.
    longest = {}
    for name, spec in params.items():
        if spec.get("type", "string") == "string" and spec.get("pattern"):
            longest[name] = next((("a" * n) for n in range(80, 0, -1)
                                  if re.fullmatch(spec["pattern"], "a" * n)), "a")
    defaults = {n: str(s["default"]) for n, s in params.items() if isinstance(s.get("default"), str)}
    for label, values in (("defaults", defaults), ("longest inputs", {**defaults, **longest})):
        def render(text):
            return re.sub(r"\{(\w+)\}", lambda m: values.get(m.group(1), m.group(0)), text)
        for k, r in t["resources"].items():
            if r.get("type") != "agent":
                continue
            agent_name = render(r.get("name", ""))
            check(bool(AGENT_NAME.fullmatch(agent_name)), f"agent {k}: name {agent_name!r} ({label}) is not a valid Switch agent name")
            shown = render(r.get("display_name", ""))
            check(len(shown) <= 64, f"agent {k}: display_name is {len(shown)} chars with {label} (Switch max 64)")
    res = t["resources"]
    check(sum(1 for r in res.values() if r.get("type") == "group") <= 1, "a template creates at most one group")
    allowed = {"agent": AGENT_KEYS, "room": ROOM_KEYS, "group": GROUP_KEYS}
    for k, r in res.items():
        kind = r.get("type")
        check(kind in allowed, f"resource {k}: type must be agent, room or group")
        if kind in allowed:
            check(set(r) <= allowed[kind], f"{kind} {k}: key(s) Switch does not read {sorted(set(r) - allowed[kind])}")
        check(bool(r.get("name") or (kind == "agent" and r.get("display_name"))), f"resource {k} needs a name")
        if kind == "room":
            check(r.get("channel_type", "channel_public") in {"channel_public", "channel_private"},
                  f"room {k}: bad channel_type")
            for d in r.get("docs", []):
                check({"name", "description", "instructions", "content"} <= set(d),
                      f"room {k}: doc {d.get('name')} needs name, description, instructions and content")
        for cond in ([r["if"]] if "if" in r else []) + list(conditional_values(r)):
            m = CONDITION.match(str(cond))
            check(bool(m), f"resource {k}: {cond!r} is not a Switch condition")
            if m:
                check(m.group(1) in params, f"resource {k}: condition reads undeclared param {m.group(1)}")


def check_template():
    b0 = len(errors)
    built = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_template.py"), "--check"],
                           capture_output=True, text=True)
    check(built.returncode == 0, "festcommand.template.yaml is stale. Run: python scripts/build_template.py")
    try:
        import yaml  # type: ignore
    except ImportError:
        print("  ⚠ PyYAML not installed: skipping structural template checks (pip install pyyaml)")
        done("template is up to date with its sources", b0)
        return
    t = yaml.safe_load((ROOT / "festcommand.template.yaml").read_text(encoding="utf-8"))
    check(t.get("version") == 2, "template should be version 2")
    check(not ({"agents", "rooms", "groups", "kickoff"} & set(t)), "v2 template must not use top-level agents/rooms/groups/kickoff")
    check_switch_schema(t)
    res = t["resources"]
    params = set(t.get("params", {}))
    kinds = {k: r.get("type") for k, r in res.items()}
    check(all(re.fullmatch(r"[A-Za-z0-9_]+", k) for k in res), "resource keys must be letters, digits, _")
    for k, r in res.items():
        if r["type"] == "agent":
            for f in AGENT_REQUIRED:
                check(bool(r.get(f)), f"agent {k} is missing {f}")
            check(bool(r.get("machine") or r.get("location")), f"agent {k} needs machine or location")
            a = r.get("addressing", "owner")
            if isinstance(a, dict):
                for room in a.get("anyone_in", []):
                    check(kinds.get(room) == "room", f"agent {k}: anyone_in references unknown room {room}")
            else:
                check(a in ADDRESSING, f"agent {k}: bad addressing {a!r}")
        elif r["type"] == "room":
            for ag in r.get("agents", []):
                check(kinds.get(ag) == "agent", f"room {k}: unknown agent {ag}")
            check(kinds.get(r.get("group")) == "group", f"room {k}: group {r.get('group')!r} is not a group resource")
            check("users" in r and "people" not in r, f"room {k}: use users:, not people:")
            for d in r.get("docs", []):
                check(set(d) <= {"name", "description", "instructions", "content"}, f"room {k}: doc has unknown keys")
                check(bool(d.get("content")), f"room {k}: doc {d.get('name')} is empty")
                # Switch has no brace escape, so a doc must not contain anything
                # placeholder-shaped: {param}, {key.name} or {$builtin}.
                hits = sorted(set(PLACEHOLDER.findall(d.get("content", ""))))
                check(not hits, f"room {k}: doc {d['name']} contains placeholder(s) {hits} that Switch would substitute")
            if r.get("kickoff"):
                check(bool(re.search(r"@\{(\w+)\.name\}", r["kickoff"])), f"room {k}: kickoff mentions no agent")
                # Agents can only update documents they created, so live state is
                # an agent-created copy made at kickoff. Switch needs room-unique
                # names, and the baseline being copied must be in the same room.
                provisioned = {d["name"] for d in r.get("docs", [])}
                for live in re.findall(r"no\s+([\w.]+\.(?:json|md))\s+yet", r["kickoff"]):
                    check(live not in provisioned, f"room {k}: kickoff creates {live}, which the template already provisions")
                for base in re.findall(r"exact\s+content\s+of\s+([\w.]+\.(?:json|md))", r["kickoff"]):
                    check(base in provisioned, f"room {k}: kickoff copies {base}, which is not a document in this room")
        elif r["type"] == "group":
            for l in r.get("links", []):
                check(kinds.get(l["from"]) == "room" and kinds.get(l["to"]) == "room", f"group {k}: bad link {l}")
    # Each agent must be in a room with every agent it hands off to.
    rooms_of = {k: {rk for rk, r in res.items() if r["type"] == "room" and k in r.get("agents", [])}
                for k, r in res.items() if r["type"] == "agent"}
    for k in rooms_of:
        check(bool(rooms_of[k]), f"agent {k} is in no room")
    for k, r in res.items():
        if r["type"] == "agent":
            for other in re.findall(r"@\{(\w+)\.name\}", r["instructions"]):
                check(bool(rooms_of[k] & rooms_of.get(other, set())),
                      f"agent {k} mentions @{other} but they share no room")
    told = [r.get("instructions", "") for r in res.values()] + [r.get("kickoff", "") for r in res.values()]
    named = {op for t in told for op in OPERATION_LIKE.findall(t or "")}
    check(named <= SWITCH_OPERATIONS, f"instructions name Switch operations that don't exist: {sorted(named - SWITCH_OPERATIONS)}")
    text = (ROOT / "festcommand.template.yaml").read_text(encoding="utf-8")
    refs = set(re.findall(r"\{(\w+)\.name\}", text))
    check(refs <= set(res), f"unknown resource references: {sorted(refs - set(res))}")
    known = {"{" + p + "}" for p in params} | {"{" + r + ".name}" for r in res} | {"{$" + b + "}" for b in BUILTINS}
    unknown = sorted(set(PLACEHOLDER.findall(text)) - known)
    check(not unknown, f"placeholders that are neither params, resource names nor Switch built-ins: {unknown}")
    done(f"template: {sum(1 for v in kinds.values() if v == 'agent')} agents, "
         f"{sum(1 for v in kinds.values() if v == 'room')} rooms, 1 group, all references resolve", b0)


def main() -> int:
    print("🎮 FestCommand validation")
    try:
        bracket, ledger, schedule = load()
    except (OSError, json.JSONDecodeError) as e:
        print(f"✗ could not load documents: {e}")
        return 1
    section("Template")
    check_template()
    section("Schedule ↔ bracket")
    check_schedule_vs_bracket(bracket, schedule)
    section("Bracket")
    check_bracket(bracket)
    section("Ledger ↔ rulebook")
    check_ledger(ledger, schedule)
    print()
    if errors:
        print(f"✗ {len(errors)} problem(s), {passes} checks passed")
        return 1
    print(f"✅ All {passes} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
