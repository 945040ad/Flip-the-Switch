# 🎮 FestCommand

> Multi-Room Esports, Sponsorship & Event Ops War Room — powered by [Switch](https://github.com/sandbox-quantum/switch)

[![Built for Flip the Switch Hackathon](https://img.shields.io/badge/Flip%20the%20Switch-2026-blue)]()
[![Track 01](https://img.shields.io/badge/Track-Best%20Business%20Workflow-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## The Problem

Organizing a massive campus tech fest, hackathon, or esports tournament (with BGMI/Valorant brackets, sponsor booths, cosplay competitions, and merch) usually collapses into **chaotic WhatsApp/Discord groups** where:

- 😤 Nobody knows the latest schedule change
- 🔥 Match disputes turn into flame wars
- 💸 Budget approvals get lost in 500+ unread messages
- 🤷 Sponsors don't know if their deliverables were completed
- 😵 The fest lead is drowning in DMs instead of running the event

You end up with 12 WhatsApp groups, zero accountability, and a festival that runs on vibes instead of process.

---

## The Solution: FestCommand

FestCommand turns your Discord, Slack, or Mattermost server into a **structured event-operations war room**. It is one Switch template that creates:

- **three rooms** with different visibility: a public helpdesk, a private ops room, and a private finance room;
- **three AI agents** with different reach: who can address each one is set per agent;
- **room documents** the agents work from: the schedule & rulebook, the bracket and the sponsor ledger, which each agent turns into **live copies only it can edit**;
- **a human approval gate**: no result, ruling, schedule change, or rupee moves until the Fest Lead types `approve <TYPE>-<ID> #<code>`.

---

## Architecture

```
   #public-helpdesk  (public)          #tournament-ops  (private)          #sponsor-finance  (private)
  ┌───────────────────────┐          ┌───────────────────────────┐        ┌────────────────────────┐
  │ 👥 participants        │          │ 🧑 Fest Lead               │        │ 🧑 Fest Lead            │
  │                       │ reports  │                           │ "tour- │                        │
  │ 🤖 concierge ─────────┼─────────►│ 🤖 concierge               │ nament │ 🤖 sponsor-tracker     │
  │                       │◄─────────┤ 🤖 bracket-marshal         │ done"  │                        │
  │                       │ approved │ 🤖 sponsor-tracker ────────┼───────►│                        │
  │ 📄 schedule_and_rules │ outcomes │                           │        │ 📄 sponsor_ledger.json │
  │ ✏️ announcements.md    │          │ 📄 bracket_state.json      │        │ ✏️ ledger_live.json     │
  │                       │          │ 📄 schedule_and_rules.md   │        │ ✋ approve PAYOUT-01 #… │
  │                       │          │ ✏️ bracket_live_<game>.json │        │ ✋ approve VENDOR-03 #… │
  │                       │          │ ✋ approve MATCH-06 #…     │        │                        │
  └───────────────────────┘          └───────────────────────────┘        └────────────────────────┘
                     group "TechStorm 2026 FestCommand": links helpdesk ⇄ ops → finance
   📄 provisioned by the template, read-only to every agent · ✏️ created at kickoff by the one agent that can edit it
```

| Agent | Rooms | Addressing (who can make it act) | Writes |
|---|---|---|---|
| `{fest}-concierge` | helpdesk, ops | `anyone_in: [helpdesk, ops]` | `announcements.md`: approved outcomes only |
| `{fest}-bracket-marshal` | ops | `owner-agents`: the Fest Lead and their agents | `bracket_live_<game>.json` + `approvals_live.json`, after approval |
| `{fest}-sponsor-tracker` | ops, finance | `owner-agents` | `ledger_live.json`, after approval |

**How hand-offs cross rooms.** An agent that is a member of two rooms is the bridge between them. The concierge carries a participant's report from the helpdesk into ops, and carries the approved outcome back out. The sponsor tracker hears "tournament complete" in ops and opens payouts in finance, the only room where money is discussed. Every Switch agent operation acts on the one room a session is connected to. So an agent crosses with `list_linked_rooms` (which returns the group's labelled `links:`) and `connect_to_room`, and addresses the next agent with `send_targeted_message`.

**Who can write what is enforced by Switch, not just by instructions.** Switch lets only the agent that *created* a room document update it, and documents a template provisions have no creating agent. So the template's documents are a read-only baseline, and at kickoff each stateful agent copies its document into documents it owns. The marshal splits the bracket into one `bracket_live_<game>.json` per tournament plus `approvals_live.json`, so each approval rewrites a few KB and a bad write can only damage one game. The tracker keeps `ledger_live.json`. The concierge does the same with `announcements.md`, a public log of approved changes. No other agent, and no participant, can alter them.

**Why the public can't tamper with results.** Participants can address only the concierge, and the concierge only files reports. The bracket marshal and sponsor tracker use `owner-agents` addressing, so no participant can talk to them at all. On top of that, the agents' instructions accept an `approve` line only when the Fest Lead typed it. An approval relayed by any agent doesn't count.

### Data flow

```
Question  ─► concierge reads announcements.md, then the rulebook ─► answer       (no human needed)

Result    ─► concierge ─► ops: marshal validates (exists? legal score? proof?)
          ─► "approve MATCH-06 #da40"  ◄── 🧑 Fest Lead
          ─► bracket_live_valorant.json updated, winner slotted into the next match, audit_log += entry
          ─► marshal: 📣 ANNOUNCE ─► concierge logs it in announcements.md and posts in helpdesk

Dispute   ─► same path; the marshal quotes the rulebook, flags rule gaps, finds a free slot for a replay

Payout    ─► marshal: 🏁 TOURNAMENT COMPLETE in ops ─► tracker opens PAYOUT-xx in finance
          ─► 🧑 approves ─► ledger_live.json: prize status, payout_log, budget recomputed
```

---

## Why Switch is essential

| Need | What Switch provides | Where in the template |
|---|---|---|
| Stand up 3 agents + 3 rooms + docs in one go, for any fest | Templates with typed params; one import creates everything and posts a kickoff into each room | `festcommand.template.yaml` (v2 `resources:`) |
| Keep participants away from the agents that change state | Per-agent `addressing` | `owner-agents` on marshal & tracker; `anyone_in` on concierge |
| Keep money out of the public agent's reach | Rooms with their own members and documents | the ledger lives only in the finance room |
| Shared state with exactly one writer | Room documents, which only their creating agent can update | template `docs:` as baseline; `*_live.json` created at kickoff |
| Move work between rooms without one all-seeing bot | Agents that belong to several rooms, plus a group with links | concierge ∈ helpdesk+ops, tracker ∈ ops+finance |
| Agents start working without anyone prompting them | Per-room `kickoff:` that mentions the agent | each room's kickoff |

---

## Verified on a live Switch server

FestCommand has been deployed and run, not just written against the docs.

| What | How it was checked | Result |
|---|---|---|
| Template accepted | Switch's own upload lint, run planner and room parser, on the newest Switch code and on the 0.31.0 server that ships with Switch Console | clean: no errors, no warnings |
| Deployed on Discord with real Claude agents | Switch Console's local server, Discord bridge, deployed from `festcommand.template.yaml` | 3 agents, 3 channels, 4 documents, 0 errors |
| Kickoffs ran unprompted | `python scripts/live_check.py inspect --console` after the deploy | each agent created its own live documents: the bracket split into 4 per-game files, the ledger copied, VENDOR-03 queued; every copy identical to the template's baseline (13/13) |
| Switch enforces the boundaries, not just the prompts | `python scripts/live_check.py protocol` drives three agents over the real agent protocol | 33/33, including **HTTP 403** when an agent writes a document it didn't create, and refusal when the marshal or concierge tries to enter the finance room |

The 403 is the design working: it is why each agent keeps its own live copy
of the documents (see [Architecture](#architecture)).

---

## Quick start

### 1. Rehearse locally (no Switch needed)

```bash
git clone https://github.com/945040ad/Flip-the-Switch.git
cd Flip-the-Switch
./scripts/setup.sh            # checks Python 3.10+, runs the validator
python scripts/rehearse.py    # ~60 s; add --fast to skip pauses
```

On Windows (PowerShell), skip `setup.sh` and run the scripts directly with `py` or `python`. No Python installed? [uv](https://docs.astral.sh/uv/) fetches one on the fly:

```powershell
uv run --no-project --with pyyaml python scripts/validate.py
uv run --no-project python scripts/rehearse.py --fast
uv run --no-project --with pyyaml python -m unittest discover -s tests
```

The scripts use only the standard library. PyYAML is optional and enables the template structure checks.

The rehearsal plays six scenarios across the three rooms **against the real documents**. Every team, time, rule and amount is read from `documents/`, approval codes are generated per request, and each approval changes the state that the next scenario reads. Use `--write OUT/` to save the post-rehearsal live documents exactly as the agents keep them in Switch (`bracket_live_<game>.json` ×4, `approvals_live.json`, `ledger_live.json`). `documents/` itself is never modified.

### 2. Deploy on Switch

**On Discord, step by step: [docs/discord-setup.md](docs/discord-setup.md)** (about 15 minutes, bot creation to working agents, with troubleshooting).

In short:

1. Install [Switch Console](https://github.com/sandbox-quantum/switch#get-started-in-two-steps), choose **Run a server on this computer**, and sign in a coding agent (Claude Code, Codex or OpenCode) under **Agent providers**.
2. Connect your messaging app (Discord, Slack, Teams, Telegram or Mattermost) under **Home → Messaging apps**, and link your own account (**This is me**).
3. **Templates → Import** `festcommand.template.yaml`. Set **Fest display name** (default "TechStorm 2026"), **Fest short name** (default `techstorm`, used in every room and agent name) and **Messaging app**. Choose the app explicitly: the field otherwise defaults to the server's first one, often the Console's built-in Mattermost.
4. Create. Switch makes the three agents, the three rooms with their documents, and the group. Each room's kickoff wakes its agent, and within a couple of minutes every stateful agent owns its live documents.

You don't need to upload any documents. They're embedded in the template.

### 3. Check the deployment

```bash
python scripts/live_check.py inspect --console    # did every kickoff create its live documents?
python scripts/live_check.py protocol --console   # does Switch enforce FestCommand's boundaries?
```

`inspect` reads your deployment. `protocol` deploys a throwaway Switch-only copy with three stand-in agents, exercises the agent protocol (who can write which document, who can enter which room, links, hand-offs), then deletes everything it made. Neither needs anything beyond the standard library. For a server not run by Switch Console, pass `--url` and `--email` and set `SWITCH_ADMIN_PASSWORD`.

### 4. Make it yours

Edit `documents/` (your schedule, teams, sponsors, budget) and `agents/*/SKILL.md` (agent behaviour), then:

```bash
python scripts/validate.py         # ~700 consistency checks; fix anything it flags
python scripts/build_template.py   # re-embed into festcommand.template.yaml
```

Day dates come from the rulebook's `## Day N Schedule — <Month> <day>` headings, and the year from the bracket's `last_updated`. Game-specific score rules (Valorant maps, BGMI points) apply only to the games you run. If your prize table uses different row labels, edit the `GAME_ROWS` mapping marked *EDIT FOR YOUR FEST* in `scripts/validate.py`.

Edit `template/festcommand.template.src.yaml`, not the generated file. CI (`.github/workflows/validate.yml`) fails if the generated template is stale or the documents contradict each other. `python -m unittest discover -s tests` breaks a throwaway copy of the project in about twenty specific ways and checks that the validator catches each one.

---

## Demo scenarios

Run `python scripts/rehearse.py`. The clock starts at the documents' snapshot, **Day 1, 17:45 IST**.

| # | Scenario | Rooms | What it shows |
|---|---|---|---|
| 1 | 📅 *"When is our final?"* (Team Mayhem) | helpdesk | Answer built from bracket + schedule: MATCH-07, Day 2 18:00, Main Stage, BO5 |
| 2 | ✅ Referee reports Valorant SF2 (MATCH-06) | helpdesk → ops → helpdesk | Validation (match exists, legal map scores incl. 14-12 OT, BO3 decided). A participant's `approve …` in public is **refused**. Fest Lead approves; Enigma Gaming slotted into the final; announced |
| 3 | ⚖️ FIFA disconnect at 1-1 in the 85th minute (MATCH-47) | helpdesk → ops → helpdesk | Marshal quotes both disconnect rules, **flags the rule gap**, recommends a rematch, finds a free Arena Alpha slot with no player clash. The Fest Lead types `pending` and gets the exact line to copy; a wrong approval code is rejected |
| 4 | 💳 Day 2 catering invoice (VENDOR-03, ₹10,500) | finance | Category impact 55% → 65.5% of budget, alert resolved after approval |
| 5 | 📊 Sponsor dashboard | finance | 5 sponsors × 5 deliverables, plus *Action required*: Monster Energy 0/2 posts due tonight, Logitech swag **overdue** vs its 15:00 ETA |
| 6 | 💰 BGMI finishes → payouts | ops → finance | ⏩ Day 2. Podium from cumulative points (rounds 2-3 simulated from a fixed seed), 3 PAYOUT approvals, ledger and budget recomputed |

---

## Project structure

```
Flip-the-Switch/
├── festcommand.template.yaml          # GENERATED: import this into Switch
├── template/
│   └── festcommand.template.src.yaml  # template source (edit this)
├── agents/
│   ├── concierge/SKILL.md             # agent instructions, embedded into the template
│   ├── bracket-marshal/SKILL.md
│   └── sponsor-tracker/SKILL.md
├── documents/                         # room documents, embedded into the template
│   ├── schedule_and_rules.md          # schedule, rulebook, prizes, venue, contacts
│   ├── bracket_state.json             # 4 tournaments, 55 matches, approvals, audit log
│   └── sponsor_ledger.json            # income, budget, sponsors, prizes, vendors, alerts
├── scripts/
│   ├── build_template.py              # source + skills + documents → template
│   ├── validate.py                    # ~700 cross-document + Switch schema checks
│   ├── rehearse.py                    # six-scenario simulation, data-driven
│   ├── live_check.py                  # checks a running Switch server (inspect / protocol)
│   └── setup.sh                       # environment + validation in one command
├── tests/test_validate.py             # mutation tests: the validator catches what it claims
├── .github/workflows/validate.yml     # CI: build check, validate, rehearse, tests
├── docs/
│   ├── discord-setup.md               # bot to working agents on Discord, ~15 minutes
│   └── live-test-checklist.md         # manual end-to-end test on a local Switch
├── demo/video-script.md               # 2-minute demo video script
├── blog/devto-draft.md                # DEV.to post draft
└── LICENSE
```

---

## Sample event: TechStorm 2026

FestCommand ships with a complete dataset for **TechStorm 2026**, a 2-day fest (Dec 14–15) at a Bengaluru convention centre.

| Track | Events |
|---|---|
| 🎮 **Esports** | Valorant 5v5 (8-team LAN playoff), BGMI 20 squads × 3 rounds, FIFA 25 1v1 (32 players), Rocket League 3v3 (double elimination) |
| 💻 **Hackathon** | 24-hour build, 2–4 per team |
| 🎭 **Stage** | Cosplay showdown, DJ sets, awards ceremony |
| 🛍️ **Expo** | Sponsor booths B1–B5, merch booth B6 |
| 🤝 **Sponsors** | HyperX (Title), Monster Energy & Logitech (Gold), AMD (Silver), Jio (Connectivity) |

| Money | |
|---|---|
| Income | ₹9,88,000 (₹8,50,000 sponsorship + ₹1,38,000 tickets) |
| Expense budget | ₹6,60,000 across 7 categories (₹5,47,000 spent at snapshot) |
| Prize pool | ₹3,28,000 (esports, hackathon, cosplay) |

The data is a mid-event snapshot: Valorant SF2 played but unreported, a FIFA dispute under review, BGMI round 2 in progress, a catering invoice awaiting approval, and Monster Energy behind on social posts. `scripts/validate.py` keeps the three documents mutually consistent.

---

## The human-in-the-loop protocol

1. The agent drafts the change and records it under `pending_approvals` (in `approvals_live.json` or `ledger_live.json`) with a fresh 4-hex code.
2. It posts the request, ending in the exact line to type, e.g. `Fest Lead: approve DISPUTE-47 #f6e4`.
3. Only that exact line, **typed by the Fest Lead in that room**, applies the change. A wrong code gets "code mismatch" and nothing changes. A line relayed by another agent is ignored. `reject …` drops the request.
4. The change is written, the entry moves to `audit_log` with who approved it and when, and the announcement or next hand-off goes out.

The code is there to stop you approving the wrong item and to make the audit log easy to search. It isn't a cryptographic signature. The security boundary is Switch itself: addressing means only the Fest Lead and their own agents can talk to the agents that write state, and creator-only documents mean no one but that agent can write it.

---

## Limitations

- **The approval check itself is policy.** Switch enforces *who can write* each live document (only the agent that created it) and *who can talk to* each agent (addressing). Whether an `approve` line came from the Fest Lead is still checked by the agent's instructions. A cryptographically enforced approval would need a tool the agents call.
- **No screenshot analysis.** The marshal checks that a proof URL is present, not what the image shows.
- **Single approver.** A real deployment would split approval roles, e.g. a finance head for payouts and a tournament director for rulings.
- **No payment rails.** Payouts are recorded in the ledger. UPI or bank transfers happen outside FestCommand.
- **No game APIs.** Results are reported by referees, not pulled from Riot or Krafton.
- **Agent judgment is only as good as the model.** Switch enforces the boundaries (see [Verified on a live Switch server](#verified-on-a-live-switch-server)), but how well an agent writes a ruling or reads a schedule depends on the coding agent running it. Every state change still waits for the Fest Lead's `approve`.

---

## Built with

- **[Switch](https://github.com/sandbox-quantum/switch)**: templates, rooms, room documents, per-agent addressing, groups
- **[Claude Code](https://claude.com/claude-code)** (or Codex / OpenCode): the coding agent behind each FestCommand agent
- **Python 3.10+, standard library only** (PyYAML optional): build, validation and rehearsal scripts

---

## Hackathon

Built for the **[Flip the Switch Hackathon](https://wemakedevs.org)** by WeMakeDevs × DevTools Academy × SandboxAQ.

**Track**: Best Business Workflow ($2,000)

**Rubric alignment**:
| Criteria | Weight | How FestCommand addresses it |
|---|---|---|
| Switch Features | 30% | v2 template creating 3 agents, 3 rooms and a linked group; template docs as baseline + agent-created live docs (creator-only writes); per-agent addressing incl. `anyone_in`; per-room kickoffs; multi-room agents crossing via `list_linked_rooms`/`connect_to_room`; `send_targeted_message` hand-offs; conditional `users` so it deploys with or without a messaging app |
| Technical Execution | 25% | Runs on a live Switch server with Discord and real Claude agents; `live_check.py` reproduces the verification on any server (33 protocol + 13 deployment checks). Template built from single-source skills + documents, 700-check validator (cross-document + Switch schema) with mutation tests, data-driven rehearsal with a working approval gate, CI |
| Creativity & Impact | 25% | Solves real campus fest chaos — a pain point felt by thousands of student organizers |
| Presentation & Docs | 20% | Architecture diagram, demo video script, DEV.to blog draft, comprehensive README |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>FestCommand — Because your fest deserves better than a WhatsApp group with 347 unread messages.</i> 🎮
</p>
