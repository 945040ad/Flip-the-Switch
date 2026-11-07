# Live test on Switch: checklist

FestCommand's template and agent mechanics were checked against Switch's
server source (template linter, v2 compiler, run planner, room-document and
agent operations), and `scripts/validate.py` mirrors those rules. This
checklist covers what only a live run can prove. It takes about 20 minutes.

## 0. Set up a local Switch (no messaging app needed)

1. Install the Switch Console desktop app:
   [Windows x64 installer](https://github.com/sandbox-quantum/switch/releases/latest/download/switch-console-x64.exe)
   (other platforms: the Switch repo's README).
2. Choose **Run a server on this computer**. It needs no Docker and no
   messaging app. The bundled Mattermost is optional.
3. Make sure one coding agent is installed and signed in on this machine
   (Claude Code, Codex or OpenCode). The run refuses with
   `provider_not_installed` / `provider_login_missing` otherwise.

## 1. Import and deploy

- [ ] **Templates → import** `festcommand.template.yaml`. The form shows **no
      warnings**. (Any warning here is a bug in the template. Note its code,
      e.g. `unknown_param_field`.)
- [ ] The form asks for *Fest display name*, *Fest short name* and
      *Messaging app*; *Provider*, *Machine* and *Agents dir* sit under
      **Advanced**.
- [ ] Leave **Messaging app** empty and create. The preview shows 3 agents,
      3 rooms and 1 group.
- [ ] Created: `techstorm-concierge`, `techstorm-bracket-marshal`,
      `techstorm-sponsor-tracker`; rooms `techstorm-public-helpdesk`,
      `techstorm-tournament-ops`, `techstorm-sponsor-finance`; group
      *TechStorm 2026 FestCommand* with 3 links.

## 2. Kickoffs create the live documents

Template documents are read-only to agents (only a document's creator can
update it), so each agent makes its own live copy at kickoff.

- [ ] **helpdesk**: the concierge posts a welcome and the room gains
      `announcements.md`.
- [ ] **ops**: the marshal posts a status, and the room gains
      `bracket_live_valorant.json`, `bracket_live_bgmi.json`,
      `bracket_live_fifa25.json`, `bracket_live_rocket_league.json` and
      `approvals_live.json`. Spot-check one against `bracket_state.json`:
      the tournament's object should be identical.
- [ ] **finance**: the tracker posts the sponsor dashboard, and the room
      gains `ledger_live.json`.
- [ ] Re-trigger a kickoff (or restart an agent). No duplicate documents
      appear: each kickoff creates only the live documents the room doesn't
      have yet.

## 3. The approval gate (ops)

Post as the Fest Lead in `techstorm-tournament-ops`:

- [ ] Ask the concierge, in helpdesk, to report: *"MATCH-06 done. Enigma
      Gaming beat GodLike Esports 2-1: Bind 13-9, Haven 10-13, Ascent 14-12.
      Proof: https://example.com/sf2.png"*. The concierge hands it to the
      marshal in ops (look for the `@techstorm-bracket-marshal` mention).
- [ ] The marshal shows ✓/✗ checks and ends with
      `Fest Lead: approve MATCH-06 #xxxx`.
- [ ] Type `pending`. You get one line per open request, with the exact line
      to copy.
- [ ] Type the line with a **wrong** code. You get "code mismatch" and
      nothing changes.
- [ ] Type the right line. Then:
  - [ ] `bracket_live_valorant.json` shows MATCH-06 completed and Enigma
        Gaming slotted into MATCH-07.
  - [ ] `approvals_live.json` moved the entry to `audit_log`.
  - [ ] **No other** `bracket_live_*.json` changed.
  - [ ] The concierge appends a line to `announcements.md` and posts
        📢 BRACKET UPDATE in helpdesk.

## 4. Boundaries hold

- [ ] In helpdesk, a participant (or you, in a second account) writes
      `approve MATCH-06 #xxxx`. The concierge refuses to relay it.
- [ ] Mention `@techstorm-bracket-marshal` from helpdesk. It does not answer:
      `owner-agents` addressing, and it isn't in that room.
- [ ] Ask the concierge about the budget or a vendor invoice. It declines.
- [ ] From finance, ask the tracker to post budget figures in ops. It
      declines.

## 5. Money (finance)

- [ ] Ask the tracker about VENDOR-03 (Day 2 catering). It opens a VENDOR
      request showing the category moving from 55% to 65.5%.
- [ ] Approve it. `ledger_live.json` updates `spent`, `utilization_pct`,
      `expenses.summary`, `total_spent` and `budget_utilization_pct`, and
      appends to `audit_log`.

## If something fails

Note the step, the agent's last message, and any tool error (e.g.
`PermissionError … did not create document`). Most fixes are a line in
`agents/*/SKILL.md` or `template/festcommand.template.src.yaml`. Then:

```bash
python scripts/build_template.py && python scripts/validate.py
```

and import the new `festcommand.template.yaml`. For a clean retest,
delete the earlier run's agents and rooms first.
