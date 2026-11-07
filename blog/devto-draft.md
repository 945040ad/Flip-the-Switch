---
title: "How I Built FestCommand — A Multi-Room Esports War Room on Switch"
published: false
description: "Three AI agents, three chat rooms, one command center. Here's how I turned campus fest chaos into a structured ops war room using Switch's multi-agent orchestration."
tags: switch, hackathon, ai, devops
cover_image: https://via.placeholder.com/1000x420/1a1a2e/eee?text=FestCommand+%E2%80%94+Multi-Room+Esports+War+Room
canonical_url:
series: "Flip the Switch Hackathon"
---

# How I Built FestCommand — A Multi-Room Esports War Room on Switch

Last semester, I helped organize a campus tech fest with 2,000 attendees. We had four esports tournaments, a 24-hour hackathon, cosplay competitions, five sponsors, and a merch booth.

We managed everything through 12 WhatsApp groups.

It was a disaster.

Match disputes turned into flame wars. Budget approvals disappeared in 500+ unread messages. The Valorant bracket was wrong for three hours because someone updated the wrong spreadsheet. Our title sponsor asked four times whether their logo was on the stream overlay. The fest lead — me — spent the entire event buried in DMs instead of actually running anything.

So when I saw the [Flip the Switch Hackathon](https://wemakedevs.org) and its "Best Business Workflow" track, I knew exactly what to build.

## What is FestCommand?

FestCommand is a **multi-room AI-powered event operations war room** built on [Switch](https://github.com/sandbox-quantum/switch). It replaces the chaos of group chats with three structured rooms, three specialized AI agents, and a human approval gate on every decision that changes a result or moves money.

Think of it as mission control for your fest — except the mission controllers are AI agents that never sleep, never miss a message, and always follow the rules you set.

### The Three Rooms

```
   #public-helpdesk  (public)          #tournament-ops  (private)         #sponsor-finance  (private)
  ┌──────────────────────┐          ┌──────────────────────────┐        ┌───────────────────────┐
  │ participants         │ reports  │ Fest Lead                │ payout │ Fest Lead             │
  │ @concierge ──────────┼─────────►│ @concierge               │ trigger│ @sponsor-tracker      │
  │                      │◄─────────┤ @bracket-marshal         ├───────►│                       │
  │                      │ approved │ @sponsor-tracker         │        │ 📄 sponsor_ledger.json│
  │                      │ results  │ 📄 bracket_state.json    │        │                       │
  │                      │          │ 📄 schedule_and_rules.md │        │                       │
  └──────────────────────┘          └──────────────────────────┘        └───────────────────────┘
```

1. **`#public-helpdesk`**: open to everyone. The concierge answers questions from the live schedule, takes match results and dispute reports, and announces approved outcomes. It's the information desk at the venue entrance.

2. **`#tournament-ops`**: private. The bracket marshal validates results, rules on disputes against the rulebook, and proposes schedule shifts. Nothing changes until the fest lead approves.

3. **`#sponsor-finance`**: private. The sponsor tracker keeps the ledger: sponsor deliverables, budget burn per category, vendor invoices and prize payouts. Every rupee movement needs approval.

## Why Switch?

FestCommand is not one bot with access to everything. It's three agents with **different reach**, and Switch is what draws those boundaries. These are the Switch features it uses:

### 1. One template creates the whole topology

The entire war room is one file, `festcommand.template.yaml`, in Switch's v2 template language. It defines three agents, three rooms and a group that links them. You import it in Switch Console and fill in a fest name and a messaging app. Switch then creates everything in one pass and posts a kickoff into each room, so all three agents start working immediately.

```yaml
version: 2
params:
  fest: { type: string, default: techstorm, pattern: "[a-z][a-z0-9-]*" }
  bridge: { type: bridge, default: [$first] }
  # provider, machine, agents_dir …

resources:
  concierge:
    type: agent
    name: "{fest}-concierge"
    addressing: { anyone_in: [helpdesk, ops] }
    instructions: |
      …contents of agents/concierge/SKILL.md…

  bracket_marshal:
    type: agent
    name: "{fest}-bracket-marshal"
    addressing: owner-agents
    # …

  war_room:
    type: group
    links:
      - { from: helpdesk, to: ops, label: "disputes & match results" }
      - { from: ops, to: helpdesk, label: "approved announcements" }
      - { from: ops, to: finance, label: "tournament complete → payouts" }

  ops:
    type: room
    group: war_room
    channel_type: channel_private
    agents: [bracket_marshal, concierge, sponsor_tracker]
    users: ["{$creator}"]
    docs:
      - name: bracket_state.json
        content: |
          …contents of documents/bracket_state.json…
    kickoff: |
      @{bracket_marshal.name} you're live. Post a one-screen status…
```

The agent instructions and the room documents live in their own files (`agents/*/SKILL.md`, `documents/*`). A small build script inlines them into the template, so the instructions an agent runs with and the document it reads can never drift from what's in the repo.

### 2. Addressing is the security boundary

Addressing is set **per agent**, and it decides who can make that agent act:

| Agent | Addressing | Who can trigger it |
|---|---|---|
| concierge | `{anyone_in: [helpdesk, ops]}` | any participant in the helpdesk, plus the ops room |
| bracket-marshal | `owner-agents` | only the fest lead and the fest lead's other agents |
| sponsor-tracker | `owner-agents` | only the fest lead and the fest lead's other agents |

So a participant can't message the bracket marshal at all, let alone prompt-inject it into changing a result. The only path from the public into ops goes through the concierge, and the concierge files *reports*. It can't make rulings.

### 3. Rooms scope the documents

Each room carries its own documents (`docs:` in the template). The bracket and the rulebook live in `#tournament-ops`. The money lives in `#sponsor-finance`, a room the concierge isn't in, so sponsor commitments and vendor invoices are never in the public agent's reach.

### 4. Cross-room hand-offs come from membership

An agent that sits in two rooms is the bridge between them. The concierge is in both helpdesk and ops, so it carries a dispute report into ops and carries the approved ruling back out. The sponsor tracker is in both ops and finance, so it hears "tournament complete" and opens payouts where the money is. The group's `links:` draw those flows on the room map.

### 5. The human gate

Every state change waits for the fest lead to type an exact line:

```
approve DISPUTE-47 #f6e4
```

The code is fresh for each request, so you can't approve the wrong item by accident, and each request plus its approval lands in an `audit_log` inside the document. The gate is enforced by the agents' instructions, and Switch's addressing backs it up. The marshal and tracker accept an approval only when the fest lead typed it, never one relayed by another agent. Participants can't address them at all.

## The Scenarios

The rehearsal script (`python scripts/rehearse.py`) plays six scenarios against the real documents. Every team, time, rule and rupee comes from the data files, and each approval changes the state that the next scenario reads.

1. **Schedule question 📅**: Team Mayhem asks when the Valorant final is. The concierge answers from the bracket and the schedule: MATCH-07, Day 2 18:00, Main Stage, BO5.
2. **Match result ✅**: a referee reports Semifinal 2. The marshal checks the match exists, the map scores are legal Valorant scores and the series is decided, then asks for approval. A random participant tries `approve MATCH-06 #…` in the public room and gets refused. The fest lead approves, the winner is slotted into the grand final, and the concierge announces it.
3. **A dispute the rules don't cover ⚖️**: a FIFA player disconnects at 1-1 in the 85th minute. The rulebook only covers disconnects *before* the 20th minute, or after it *with a leader*. The marshal quotes both rules, flags the gap as a judgment call, recommends a full rematch, and finds a free slot in the schedule. A wrong approval code is rejected. The right one goes through.
4. **Vendor payment 💳**: Day 2 catering (₹10,500). The tracker shows the category going from 55% to 65.5% and confirms it stays under the 80% warning line.
5. **Sponsor dashboard 📊**: deliverables for all five sponsors, plus an action list. Monster Energy's 0/2 social posts are due tonight. Logitech's swag ETA was 15:00 and is now overdue.
6. **Payouts 💰**: fast-forward to Day 2. BGMI finishes, the marshal posts the podium in ops, and the tracker opens three PAYOUT requests in finance with the rulebook's PAN/TDS conditions.

## Keeping the data honest

Agents answer from documents, so a contradiction between documents becomes a confidently wrong answer in chat. `scripts/validate.py` runs 580 checks. It checks that every match in the published schedule exists in the bracket at the same time and stage, and that winners flow into the right next match. It checks that Valorant map scores are legal and BGMI points add up. It checks that the ledger's arithmetic holds, that the budget isn't over-allocated, that prize amounts match the rulebook's prize table, and that booth numbers match the venue map. It also checks that the template's references resolve, and that no embedded document contains a `{placeholder}` Switch would rewrite (Switch has no brace escape). CI runs it on every push.

## What I Learned

### 1. Room topology is an underrated design primitive

Most people think about AI agents as individual entities. Switch made me think about **rooms**: bounded contexts where specific agents operate with specific reach over specific documents. That's closer to how real organizations work. The finance team doesn't sit in the customer support room.

### 2. Human-in-the-loop is a feature, not a limitation

My first instinct was to automate everything. But for high-stakes decisions like match rulings and prize payouts, you **want** a human gate. The agent does the investigation and the paperwork. The human makes the judgment call.

### 3. Addressing is where security actually lives

I almost set everything to `anyone` for simplicity. Then I realized any participant could talk the bracket marshal into "correcting" a score. With `owner-agents` on the marshal, the attack surface is one agent (the concierge) that is only allowed to file reports.

### 4. Your documents are your prompt

The agents are only as right as the data they read. My first sample data had the booths swapped between two files and a pending invoice counted as spent. It also had two different prize tables. A validator caught all of it. Write one.

## Limitations

- **No image analysis**: the marshal checks that a proof URL exists but can't read the score in the image.
- **The approval gate is policy, not platform**: it's enforced by agent instructions plus addressing, not by a Switch primitive. A cryptographic approval would need a tool the agents call.
- **Single approver**: one fest lead. A real deployment wants a finance head for payouts and a tournament director for rulings.
- **No payment integration**: payouts are recorded in the ledger, and the UPI/bank transfer happens outside FestCommand.
- **No game API integration**: results are submitted by referees, not pulled from Riot or Krafton.

## Try It Yourself

```bash
git clone https://github.com/945040ad/Flip-the-Switch.git
cd Flip-the-Switch

./scripts/setup.sh                    # checks Python, runs the validator
python scripts/rehearse.py            # all six scenarios, no Switch needed

# Deploy: Switch Console → Templates → import festcommand.template.yaml
```

## Wrapping Up

FestCommand started from real pain. I've been that fest lead drowning in WhatsApp groups, manually copying bracket results between chats, chasing sponsors for deliverable updates, and losing dispute resolutions in a sea of unread messages.

Switch gave me the primitives to build something better: **rooms** for bounded contexts, **room documents** for shared state, **per-agent addressing** for security, **templates** to stand the whole thing up in one pass, and an agent in two rooms as the bridge between them. The human gate on top makes it trustworthy.

Three rooms. Three agents. One command center. That's FestCommand.

---

**GitHub**: [github.com/945040ad/Flip-the-Switch](https://github.com/945040ad/Flip-the-Switch)
**Hackathon**: [Flip the Switch 2026](https://wemakedevs.org) — Best Business Workflow Track
**Built with**: [Switch](https://github.com/sandbox-quantum/switch) + Claude Code

*If you've ever organized a fest and felt the chaos, give it a ⭐ — or better yet, fork it and run your next event on FestCommand.*
