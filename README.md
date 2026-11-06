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

FestCommand turns your Discord server into a **structured, AI-powered event operations war room** using Switch's multi-room orchestration.

**Three specialized rooms. Three AI agents. One command center.**

Each room has a clear purpose, scoped permissions, shared documents, and AI agents that coordinate across rooms — with human approval gates at every critical decision.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FestCommand on Switch                         │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     #public-helpdesk                              │  │
│  │                   addressing: anyone                              │  │
│  │                                                                   │  │
│  │   👥 Participants ──► @concierge-agent                           │  │
│  │                        │                                          │  │
│  │   📄 schedule_and_rules.md                                       │  │
│  │                        │                                          │  │
│  │   Functions:           │                                          │  │
│  │   • Answer FAQs        │   ┌─── Dispute escalation ──────┐       │  │
│  │   • Share schedules    │   │                              │       │  │
│  │   • Announce results   ◄───┼── Resolution announcements   │       │  │
│  │   • Escalate disputes ─┼───┘                              │       │  │
│  └────────────────────────┼──────────────────────────────────┼───┘  │
│                           │                                  │       │
│           ┌───────────────▼──────────────────────────────────▼──┐   │
│           │                  #tournament-ops                     │   │
│           │               addressing: owner-agents               │   │
│           │                                                      │   │
│           │   🧑 Fest Lead + @bracket-marshal + @sponsor-tracker │   │
│           │                                                      │   │
│           │   📄 bracket_state.json                              │   │
│           │   📄 schedule_and_rules.md                           │   │
│           │                                                      │   │
│           │   Functions:                                         │   │
│           │   • Validate match results (proof required)          │   │
│           │   • Investigate & resolve disputes                   │   │
│           │   • Update brackets (after human approval)           │   │
│           │   • Schedule changes                                 │   │
│           │                                                      │   │
│           │   Approval: "approve MATCH-14 #a8f2"                │   │
│           │   Approval: "approve DISPUTE-05 #c4d1"              │   │
│           │             │                                        │   │
│           └─────────────┼────────────────────────────────────┘   │
│                         │                                         │
│              Prize payout triggers                                │
│                         │                                         │
│           ┌─────────────▼────────────────────────────────────┐   │
│           │              #sponsor-finance                      │   │
│           │           addressing: owner-agents                 │   │
│           │                                                    │   │
│           │   🧑 Fest Lead + @sponsor-tracker                  │   │
│           │                                                    │   │
│           │   📄 sponsor_ledger.json                           │   │
│           │                                                    │   │
│           │   Functions:                                       │   │
│           │   • Prize pool payouts                             │   │
│           │   • Budget monitoring & alerts                     │   │
│           │   • Vendor payment tracking                        │   │
│           │   • Sponsor deliverable dashboards                 │   │
│           │                                                    │   │
│           │   Approval: "approve PAYOUT-03 #b7e9"             │   │
│           └────────────────────────────────────────────────┘   │
│                                                                  │
│  Cross-Room Flows (via Switch Group Links):                      │
│  ─────────────────────────────────────────                       │
│  #public-helpdesk ◄──► #tournament-ops   (dispute escalation     │
│                                           + bracket announces)   │
│  #tournament-ops  ───► #sponsor-finance  (prize payout triggers) │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

```
Participant question ──► @concierge reads schedule_and_rules.md ──► Instant answer

Match result ──► @bracket-marshal validates proof
             ──► Posts approval request in #tournament-ops
             ──► 🧑 Fest Lead approves
             ──► bracket_state.json updated
             ──► @concierge announces in #public-helpdesk

Dispute ──► @concierge formats & escalates to #tournament-ops
        ──► @bracket-marshal investigates
        ──► 🧑 Fest Lead approves ruling
        ──► bracket_state.json updated
        ──► @concierge announces resolution in #public-helpdesk

Prize payout ──► @sponsor-tracker calculates from bracket_state.json
             ──► Posts approval in #sponsor-finance
             ──► 🧑 Fest Lead approves
             ──► sponsor_ledger.json updated
```

---

## Why Switch is Essential (Not Optional)

FestCommand **cannot work** without Switch. Here's why:

| Feature | Without Switch | With Switch (FestCommand) |
|---|---|---|
| **Multi-room linking** | Agents can't see or post across channels | Agents hand off structured data between rooms via group links |
| **Room-scoped documents** | No shared persistent memory | `bracket_state.json` and `sponsor_ledger.json` are live, versioned, shared across agents |
| **Addressing policies** | Anyone can prompt-inject the ops agent | `addressing: owner-agents` on bracket-marshal blocks unauthorized access |
| **Human-in-the-loop** | No approval gates | `approve MATCH-14 #a8f2` pattern with audit trail |
| **Cross-room notifications** | Copy-paste between channels | Bracket updates auto-announced in helpdesk when approved in ops |
| **Template portability** | Manual setup per event | One YAML template → spin up a war room for any fest in minutes |

Switch provides the **infrastructure** — room topology, document sharing, addressing rules, and cross-room message routing — that makes FestCommand's multi-agent coordination possible. Without it, you're back to one monolithic bot in one channel with no structure, no approval flow, and no scoped access.

---

## Rooms & Agents

### Room 1: `#public-helpdesk`

| Property | Value |
|---|---|
| **Agent** | `@concierge-agent` |
| **Addressing** | `anyone` — open to all participants |
| **Purpose** | Answer participant questions, announce bracket updates, escalate disputes |
| **Documents** | `schedule_and_rules.md` |

The concierge is the **public face** of FestCommand. It answers questions from the live schedule document, formats dispute reports, and announces bracket results — but it **never** makes operational decisions. Those are escalated.

### Room 2: `#tournament-ops`

| Property | Value |
|---|---|
| **Agents** | `@bracket-marshal` + `@sponsor-tracker` |
| **Addressing** | `owner-agents` — only fest lead and agents can post |
| **Purpose** | Validate match results, resolve disputes, manage schedule changes |
| **Documents** | `bracket_state.json`, `schedule_and_rules.md` |

The ops room is the **nerve center**. The bracket-marshal validates match results (requiring screenshot proof URLs), investigates disputes, and proposes resolutions — but **every state change** requires explicit fest lead approval via the `approve` command.

### Room 3: `#sponsor-finance`

| Property | Value |
|---|---|
| **Agent** | `@sponsor-tracker` |
| **Addressing** | `owner-agents` — restricted to fest lead and agent |
| **Purpose** | Prize payouts, budget monitoring, vendor payments, sponsor deliverable tracking |
| **Documents** | `sponsor_ledger.json` |

The finance room handles the money. The sponsor-tracker calculates prize distributions from bracket results, tracks sponsor deliverables, monitors budget burn rates, and generates status dashboards — with **all payouts requiring fest lead approval**.

---

## Demo Scenarios

The rehearsal script ([`scripts/rehearse.py`](scripts/rehearse.py)) walks through 5 real-world scenarios:

### 1. 📅 Schedule Question
> A participant asks: "When is the Valorant semifinal?"

The concierge agent reads `schedule_and_rules.md` and responds with the exact time, map pool, and check-in instructions — no human intervention needed.

### 2. ✅ Match Validation
> A referee submits: "TeamAlpha beat TeamBeta 13-7 on Ascent" with a screenshot URL.

The bracket-marshal validates the proof exists, checks the match ID against `bracket_state.json`, and posts an approval request. The fest lead types `approve MATCH-14 #a8f2`. The bracket updates. The concierge announces the result in helpdesk.

### 3. ⚖️ Dispute Resolution
> A player reports: "TeamGamma used a player not on their registered roster in MATCH-09."

The concierge formats a dispute report and escalates to tournament-ops. The bracket-marshal checks the roster in `bracket_state.json`, finds a violation, drafts a ruling (forfeit + warning), and requests approval. The fest lead approves. The concierge announces the resolution publicly.

### 4. 💰 Prize Payout
> The Valorant tournament concludes. Prize pool: ₹50,000.

The sponsor-tracker calculates the split (1st: ₹25,000, 2nd: ₹15,000, 3rd: ₹10,000), cross-references against the sponsor ledger, and posts a payout approval request. The fest lead approves. The ledger updates with disbursement records.

### 5. 📊 Sponsor Status
> The fest lead asks: "What's HyperX's deliverable status?"

The sponsor-tracker reads `sponsor_ledger.json` and generates a dashboard showing: booth setup ✅, logo on stream overlay ✅, product giveaway ⏳, social media shoutout ❌. Tracks completion percentage and remaining obligations.

---

## Quick Start

### Prerequisites

- [Switch](https://github.com/sandbox-quantum/switch) installed and running
- Claude Code (or any supported AI agent) enrolled in Switch
- Python 3.10+ (for rehearsal script)
- Discord server (or Slack/Mattermost)

### Run the Rehearsal (No Switch Required)

```bash
git clone https://github.com/YOUR_USERNAME/festcommand.git
cd festcommand
python scripts/rehearse.py
```

This simulates the full workflow locally with colored terminal output — no Switch instance needed.

### Deploy on Switch

1. Open the Switch Console
2. Click **Import Template** → select `festcommand.template.yaml`
3. Set your fest name (default: `techstorm`)
4. Choose your chat platform bridge (Discord / Slack / Mattermost)
5. Upload the three room documents from `documents/`
6. Click **Create Rooms** → Start chatting!

### Validate Setup

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script checks that:
- All required files exist and are valid JSON/Markdown
- The template YAML references match the document directory
- Python dependencies are satisfied

---

## Project Structure

```
festcommand/
├── festcommand.template.yaml     # Switch template — 3 rooms, 3 agents, group links
├── documents/
│   ├── schedule_and_rules.md     # Live event schedule & rules (room document)
│   ├── bracket_state.json        # Tournament bracket state
│   └── sponsor_ledger.json       # Sponsor commitments & financials
├── agents/
│   ├── concierge/
│   │   └── SKILL.md              # Concierge agent instructions
│   ├── bracket-marshal/
│   │   └── SKILL.md              # Bracket marshal instructions
│   └── sponsor-tracker/
│       └── SKILL.md              # Sponsor tracker instructions
├── scripts/
│   ├── rehearse.py               # 60-second workflow simulation
│   └── setup.sh                  # Setup validator
├── demo/
│   └── video-script.md           # Demo video script (2 min)
├── blog/
│   └── devto-draft.md            # DEV.to blog post draft
├── README.md
└── LICENSE
```

---

## Sample Event: TechStorm 2026

FestCommand ships with a complete sample dataset for **TechStorm 2026** — a 2-day campus tech fest featuring:

| Track | Events |
|---|---|
| 🎮 **Esports** | Valorant 5v5, BGMI Squad, FIFA 25 1v1, Rocket League 2v2 |
| 💻 **Hackathon** | 24-hour open track with 4 sponsor challenges |
| 🎭 **Stage** | Cosplay competition, DJ night, award ceremony |
| 🛍️ **Expo** | Merch booths, sponsor demo stations, VR arcade |
| 🤝 **Sponsors** | HyperX, Monster Energy, Logitech, AMD, Jio |

**Total prize pool**: ₹2,00,000 across all tracks
**Expected footfall**: 2,000+ participants over 2 days
**Budget**: ₹5,00,000 (tracked in `sponsor_ledger.json`)

All sample data in `documents/` is realistic and internally consistent — match IDs reference real teams, payouts reference real sponsors, and the schedule has no conflicts.

---

## The Human-in-the-Loop Flow

Every critical decision in FestCommand passes through a **human approval gate**. No AI agent can unilaterally change bracket state, disburse funds, or announce rulings.

```
Participant reports dispute in #public-helpdesk
        │
        ▼
@concierge-agent formats structured Dispute Report
  (player, match ID, category, evidence)
        │
        ▼
Escalates to @bracket-marshal in #tournament-ops
        │
        ▼
@bracket-marshal investigates:
  • Checks bracket_state.json for match details
  • Verifies roster, seed, and rule references
  • Drafts resolution with reasoning
        │
        ▼
Posts approval request:
  "⚖️ DISPUTE-05 | TeamGamma forfeits MATCH-09 (roster violation)
   Approve: approve DISPUTE-05 #c4d1"
        │
        ▼
🧑 Fest Lead reviews evidence and reasoning
  Types: "approve DISPUTE-05 #c4d1"
        │
        ▼
@bracket-marshal updates bracket_state.json
  (match result, team status, audit log entry)
        │
        ▼
Notifies @concierge-agent via cross-room link
        │
        ▼
@concierge-agent announces resolution in #public-helpdesk
  "⚖️ Ruling: TeamGamma forfeits MATCH-09 due to roster violation.
   TeamDelta advances to the quarterfinal."
```

The `#c4d1` hash is a 4-character verification code generated from the dispute content. It prevents accidental approvals of the wrong item and creates a tamper-evident audit trail.

---

## Limitations (Honest Assessment)

We believe in transparency. Here's what FestCommand **doesn't** do:

- **No real screenshot analysis**: Bracket-marshal validates that a screenshot URL exists but cannot perform image analysis to verify the actual game score. A future version could integrate vision models.
- **No live bracket visualization**: Bracket state is stored as JSON — a future version could render interactive bracket graphics (e.g., with Challonge or custom React components).
- **Single fest lead approval**: Currently only one approval flow — a production version would support role-based multi-approver chains (e.g., finance head approves payouts, tournament director approves disputes).
- **No payment gateway integration**: Payout tracking is ledger-based — actual bank/UPI transfers require manual execution outside FestCommand.
- **No real-time game API integration**: Match results are submitted manually by referees. Integration with game APIs (Riot, Krafton) would enable automatic result ingestion.

---

## Built With

- **[Switch](https://github.com/sandbox-quantum/switch)** — Multi-agent orchestration platform (rooms, documents, addressing, group links)
- **[Claude Code](https://claude.ai)** — AI agent provider powering all three agents
- **Python 3.10+** — Rehearsal simulation script
- **Markdown + JSON** — Room documents and state management

---

## Hackathon

Built for the **[Flip the Switch Hackathon](https://wemakedevs.org)** by WeMakeDevs × DevTools Academy × SandboxAQ.

**Track**: Best Business Workflow ($2,000)

**Rubric alignment**:
| Criteria | Weight | How FestCommand addresses it |
|---|---|---|
| Switch Features | 40% | Multi-room, documents, addressing policies, group links, human-in-the-loop |
| Usefulness & Impact | 20% | Solves real campus fest chaos — tested against actual event scenarios |
| Code Quality | 20% | Clean YAML template, modular agent skills, validated JSON schemas |
| Presentation & Docs | 20% | This README, demo video, blog post, rehearsal script |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>FestCommand — Because your fest deserves better than a WhatsApp group with 347 unread messages.</i> 🎮
</p>
