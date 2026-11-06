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

FestCommand is a **multi-room AI-powered event operations war room** built on [Switch](https://github.com/sandbox-quantum/switch). It replaces the chaos of group chats with three structured rooms, three specialized AI agents, and human approval gates at every critical decision.

Think of it as mission control for your fest — except the mission controllers are AI agents that never sleep, never miss a message, and always follow the rules you set.

### The Three Rooms

```
┌─────────────────────────────────────────────────────┐
│                   FestCommand                        │
│                                                      │
│  #public-helpdesk        #tournament-ops             │
│  ┌──────────────┐        ┌──────────────────┐       │
│  │ @concierge   │◄──────►│ @bracket-marshal  │       │
│  │ (anyone)     │ escal. │ @sponsor-tracker  │       │
│  │              │ + ann. │ (owner-agents)    │       │
│  └──────────────┘        └────────┬─────────┘       │
│                                   │ payouts          │
│                          ┌────────▼─────────┐       │
│                          │ #sponsor-finance   │       │
│                          │ @sponsor-tracker   │       │
│                          │ (owner-agents)     │       │
│                          └───────────────────┘       │
└──────────────────────────────────────────────────────┘
```

1. **`#public-helpdesk`** — Open to everyone. The `@concierge-agent` answers participant questions from the live schedule, announces bracket results, and escalates disputes. Think of it as the information desk at the venue entrance.

2. **`#tournament-ops`** — Restricted to the fest lead and agents only. The `@bracket-marshal` validates match results, investigates disputes, and manages brackets. The `@sponsor-tracker` handles cross-room finance triggers. No participant can message here, which prevents prompt injection and noise.

3. **`#sponsor-finance`** — Restricted. The `@sponsor-tracker` manages prize payouts, budget monitoring, vendor payments, and sponsor deliverable tracking. Every rupee is accounted for.

## Why Switch? (And Why It's Not Optional)

I want to be direct about this: FestCommand **cannot exist** without Switch. It's not a wrapper around a Discord bot. Switch provides the fundamental infrastructure that makes multi-room AI coordination possible.

Here are the specific Switch features I used and why each one matters:

### 1. Multi-Room Topology with Group Links

Switch lets me define rooms and link them together. When the concierge in `#public-helpdesk` needs to escalate a dispute, it sends a structured message through a **group link** to `#tournament-ops`. The bracket-marshal in ops receives it, processes it, and when the resolution is approved, sends the result back through the link to the helpdesk.

Without Switch, an AI agent in one Discord channel has no way to read or post in another channel. You'd need a monolithic bot with access to everything — which defeats the entire purpose of scoped rooms.

```yaml
# From festcommand.template.yaml
group-links:
  - name: helpdesk-to-ops
    rooms: [public-helpdesk, tournament-ops]
    purpose: "Dispute escalation and bracket announcements"
  - name: ops-to-finance
    rooms: [tournament-ops, sponsor-finance]
    purpose: "Prize payout triggers from completed tournaments"
```

### 2. Room-Scoped Documents

Each room has **documents** — persistent, versioned files that all agents in the room can read and write. My bracket state isn't in a Google Sheet that someone might accidentally edit. It's in `bracket_state.json`, scoped to `#tournament-ops`, and only the bracket-marshal can update it (after human approval).

```yaml
rooms:
  - name: tournament-ops
    documents:
      - bracket_state.json
      - schedule_and_rules.md
```

The concierge in `#public-helpdesk` has access to `schedule_and_rules.md` (so it can answer questions) but **not** to `bracket_state.json` (so it can't accidentally reveal unpublished results). That scoping is automatic in Switch.

### 3. Addressing Policies

This is the feature that prevents the entire thing from falling apart. In `#public-helpdesk`, the addressing is set to `anyone` — any participant can message the concierge. But in `#tournament-ops`, the addressing is `owner-agents` — only the fest lead (room owner) and the enrolled agents can post.

```yaml
rooms:
  - name: public-helpdesk
    addressing: anyone
  - name: tournament-ops
    addressing: owner-agents
```

Why does this matter? Because without it, any participant could message the bracket-marshal directly and try to manipulate match results through prompt injection. Switch's addressing policies are a **security boundary**, not just a convenience feature.

### 4. Human-in-the-Loop Approval

Every state-changing action in FestCommand requires explicit human approval. The bracket-marshal can investigate a dispute and recommend a ruling, but it **cannot** update the bracket until the fest lead types:

```
approve DISPUTE-05 #c4d1
```

The `#c4d1` hash is a 4-character verification code derived from the dispute content. It prevents the fest lead from accidentally approving the wrong item and creates a tamper-evident audit trail.

This isn't a custom hack — it's built on Switch's approval flow pattern. The agent posts a proposal, the human reviews and approves, and only then does the state change execute.

## The Five Scenarios

I built FestCommand around five real-world scenarios that I experienced (or wish I'd been prepared for) during our campus fest:

### Scenario 1: Schedule Question 📅

A participant asks "When is the Valorant semifinal?" in the public helpdesk. The concierge reads `schedule_and_rules.md` and responds with the time, venue, map pool, and check-in instructions. Zero human effort. Always accurate because it reads from the single source of truth.

### Scenario 2: Match Validation ✅

A referee submits a match result with a screenshot URL. The bracket-marshal validates the proof exists, checks the match ID against the bracket state, and posts an approval request. The fest lead approves. The bracket updates. The concierge announces the result in helpdesk. End-to-end, automated except for the approval gate.

### Scenario 3: Dispute Resolution ⚖️

A player reports a roster violation. The concierge formats a structured dispute report and escalates to tournament-ops. The bracket-marshal checks the roster data, finds the violation, drafts a ruling, and requests approval. The fest lead approves. The bracket updates. The concierge announces the resolution. Two rooms, two agents, one human gate.

### Scenario 4: Prize Payout 💰

Tournament ends. The sponsor-tracker calculates the prize split from the bracket results, cross-references the sponsor ledger to confirm funding, and posts a payout approval request. Fest lead approves. Ledger updated. No more "bro where's our prize money" in the group chat.

### Scenario 5: Sponsor Dashboard 📊

The fest lead asks "What's HyperX's deliverable status?" The sponsor-tracker reads the ledger and generates a dashboard — booth setup ✅, logo on overlay ✅, product giveaway ⏳, social media shoutout ❌. Instant accountability. No more chasing sponsor managers across WhatsApp.

## What the Template Looks Like

The entire FestCommand topology is defined in one YAML file. Here's the core structure:

```yaml
template:
  name: festcommand
  description: "Multi-room esports & event ops war room"

rooms:
  - name: public-helpdesk
    addressing: anyone
    agents:
      - concierge-agent
    documents:
      - schedule_and_rules.md

  - name: tournament-ops
    addressing: owner-agents
    agents:
      - bracket-marshal
      - sponsor-tracker
    documents:
      - bracket_state.json
      - schedule_and_rules.md

  - name: sponsor-finance
    addressing: owner-agents
    agents:
      - sponsor-tracker
    documents:
      - sponsor_ledger.json

group-links:
  - name: helpdesk-to-ops
    rooms: [public-helpdesk, tournament-ops]
  - name: ops-to-finance
    rooms: [tournament-ops, sponsor-finance]
```

That's it. Import this template into Switch, upload three documents, and you have a fully functional war room. The template is portable — change the fest name, swap the documents, and you've got a war room for a completely different event.

## What I Learned

### 1. Room topology is an underrated design primitive

Most people think about AI agents as individual entities. Switch made me think about **rooms** — bounded contexts where specific agents operate with specific permissions on specific documents. This is closer to how real organizations work. The finance team doesn't sit in the customer support room.

### 2. Human-in-the-loop is a feature, not a limitation

My first instinct was to automate everything. But after thinking about it, I realized that for high-stakes decisions (match rulings, prize payouts), you **want** a human gate. The AI does the investigation and recommendation; the human does the judgment call. That's not a limitation — it's the design.

### 3. Addressing policies are security boundaries

I almost set everything to `anyone` for simplicity. Then I realized that any participant could message the bracket-marshal and try to manipulate results. Switch's addressing policies aren't just access control — they're a security boundary that makes the whole system trustworthy.

### 4. Documents > Databases for this use case

For a 2-day fest, JSON files as room documents are perfect. They're readable, versionable, and every agent can see the same state. You don't need a database. You need a shared, scoped, versioned file — which is exactly what Switch documents provide.

## Limitations

I'm being honest about what FestCommand doesn't do:

- **No image analysis** — The bracket-marshal checks that a screenshot URL exists but can't verify the actual score in the image.
- **No live bracket graphics** — State is JSON. A future version could render visual brackets.
- **Single approver** — Only one fest lead. A production system needs role-based multi-approver chains.
- **No payment integration** — Payouts are tracked in the ledger, not executed via UPI/bank transfer.
- **No game API integration** — Match results are manually submitted, not pulled from Riot/Krafton APIs.

## Try It Yourself

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/festcommand.git
cd festcommand

# Run the rehearsal (no Switch required)
python scripts/rehearse.py

# Deploy on Switch
# 1. Open Switch Console
# 2. Import festcommand.template.yaml
# 3. Upload documents from documents/
# 4. Start chatting!
```

The rehearsal script simulates all five scenarios in your terminal with colored output. It doesn't need a Switch instance — it's a standalone demo that shows the flow.

## Wrapping Up

FestCommand started from real pain. I've been that fest lead drowning in WhatsApp groups, manually copying bracket results between chats, chasing sponsors for deliverable updates, and losing dispute resolutions in a sea of unread messages.

Switch gave me the primitives to build something better: **rooms** for bounded contexts, **documents** for shared state, **addressing** for security, **group links** for cross-room coordination, and **human-in-the-loop** for trust.

Three rooms. Three agents. One command center. That's FestCommand.

---

**GitHub**: [github.com/YOUR_USERNAME/festcommand](https://github.com/YOUR_USERNAME/festcommand)
**Hackathon**: [Flip the Switch 2026](https://wemakedevs.org) — Best Business Workflow Track
**Built with**: [Switch](https://github.com/sandbox-quantum/switch) + Claude Code

*If you've ever organized a fest and felt the chaos, give it a ⭐ — or better yet, fork it and run your next event on FestCommand.*
