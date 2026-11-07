# FestCommand Demo Video Script (2 Minutes)

> **Target length**: 1:50–2:00
> **Tone**: Energetic, relatable, technical but accessible
> **Format**: Screen recording with voiceover (no face cam required)
> **Resolution**: 1920×1080, 30fps
> **Music**: Lo-fi or upbeat electronic (low volume under voiceover)

---

## [0:00 – 0:15] Hook — The Chaos

### 🎙️ Voiceover:
> "You're running a 2,000-person campus tech fest. BGMI brackets are live, a team just filed a cheating dispute, and your title sponsor is asking about their booth setup. All of this is happening across twelve WhatsApp groups. You've got 347 unread messages. There has to be a better way."

### 📺 On Screen:
- **0:00–0:05**: Quick montage of chaotic WhatsApp/Discord screenshots (blurred or mockup):
  - Notification badges showing 99+, 200+, 347
  - Messages like "WHEN IS OUR MATCH??", "bro they cheated", "where's the prize money"
  - Scrolling walls of unread text
- **0:05–0:10**: Screen shakes slightly. Red notification banners pile up.
- **0:10–0:15**: Hard cut to black. Beat drop. FestCommand logo fades in center screen.

### 🎨 Visual Notes:
- Use split-screen effect showing 4–6 WhatsApp groups simultaneously
- Add subtle screen shake to convey overwhelm
- Logo reveal: clean white text on dark background with a subtle glow

---

## [0:15 – 0:30] What is FestCommand?

### 🎙️ Voiceover:
> "FestCommand is a multi-room AI war room built on Switch. Three rooms. Three AI agents. One command center. Instead of chaos, you get structure."

### 📺 On Screen:
- **0:15–0:20**: Switch Console → **Templates** → import `festcommand.template.yaml`. The form asks for *Fest display name*, *Fest short name* and *Messaging app* only.
- **0:20–0:25**: The YAML file briefly scrolls on screen. Highlight the three room resources with colored boxes:
  - 🟢 `#public-helpdesk` (green)
  - 🟡 `#tournament-ops` (yellow)
  - 🔴 `#sponsor-finance` (red)
- **0:25–0:30**: The three Discord channels appear in the sidebar, and each agent posts its kickoff message (welcome, bracket status, sponsor dashboard). Zoom into the channel list.

### 🎨 Visual Notes:
- Use colored labels/boxes overlaid on the YAML to match each room
- Quick zoom transitions between the three channels
- Optional: show the architecture diagram from the README for 2 seconds

---

## [0:30 – 1:00] Live Demo — Schedule Question

### 🎙️ Voiceover:
> "Let's see it in action. A player from Team Mayhem drops into the public helpdesk and asks: 'When is our Valorant final?'"
>
> *[2-second pause while the message appears]*
>
> "The concierge reads the live bracket and the schedule document and answers instantly: match, time, stage, format, check-in. All of it comes from the same documents the ops team updates."
>
> "No more 'check the pinned message.' No more 'ask in the other group.'"

### 📺 On Screen:
- **0:30–0:35**: Discord `#techstorm-public-helpdesk` is visible. A user named `@rahul_mayhem` types: *"we won our semi!! when and where is the Valorant final?"*
- **0:35–0:42**: `@techstorm-concierge` responds with a formatted message:
  ```
  GG Rahul! 🏆 Team Mayhem 2-1 Velocity Gaming

  🎮 Valorant Grand Final: MATCH-07
  • When: Day 2 (Dec 15), 18:00 IST
  • Where: Main Stage
  • Format: BO5
  • Opponent: winner of MATCH-06 (result pending)

  Check in 15 min early with your roster (5 + 1 sub). GL HF! 🎮
  ```
- **0:42–0:50**: Quick side-by-side: the `MATCH-07` entry in `bracket_live.json` (the marshal's live copy in `#tournament-ops`) and the Day 2 row of `schedule_and_rules.md` (in the helpdesk) next to the Discord reply. Draw lines from the sources to the answer.
- **0:50–1:00**: Zoom out to show the full channel. Another participant asks a different question; the concierge handles it.

### 🎨 Visual Notes:
- Use a subtle green glow/highlight on the agent's response to draw attention
- The side-by-side with the source document is key — shows it's reading from a live doc, not hallucinating
- Keep the pace brisk here — this is the simple scenario

---

## [1:00 – 1:30] Live Demo — Match Dispute + Human Approval

### 🎙️ Voiceover:
> "Now the hard case. A FIFA player's opponent disconnects at 1-1 in the 85th minute, and they want the win."
>
> *[Brief pause]*
>
> "The concierge doesn't try to resolve it — it formats a structured dispute report and escalates to tournament ops, a restricted room that participants can't access."
>
> "The bracket marshal quotes the rulebook and notices the rules don't actually cover this case. It flags that as a judgment call, recommends a rematch, finds a free slot, and asks ME. Watch."
>
> *[Pause as approval appears]*
>
> "I type 'approve DISPUTE-47' with its code. The code is unique to this request, so I can't approve the wrong thing. One line."
>
> "The bracket updates. And back in the helpdesk — the concierge announces the ruling. Two rooms, two agents, one human gate, thirty seconds."

### 📺 On Screen:
- **1:00–1:05**: In `#techstorm-public-helpdesk`, user `@TikiTaka_Pro` types: *"dispute on MATCH-47! Opponent disconnected at 1-1 in 85th minute, claims server lag. I had possession in the attacking third."*
- **1:05–1:08**: `@techstorm-concierge` responds:
  ```
  Got it. Disputes go to the ops team, who review
  within 15 minutes. I'll post the ruling here. ⚔️
  ```
- **1:08–1:12**: **Transition animation**: A message arrow flies from `#public-helpdesk` to `#tournament-ops`. Switch to the `#tournament-ops` channel view.
- **1:12–1:18**: In `#techstorm-tournament-ops`, `@techstorm-bracket-marshal` posts:
  ```
  ⚖️ DISPUTE: MATCH-47, TikiTaka_Pro vs Mbappe_Rush
  • FIFA 25: "If before 20th minute with ≤1 goal difference — rematch.
    Otherwise, leading player wins."
  ⚠️ RULE GAP: a level score at 85' isn't covered. This is a judgment call.
  Recommendation: full BO1 rematch, Day 1 20:00, Arena Alpha (free, no clashes)
  Impact: winner still plays MATCH-58, nothing downstream moves.

  Fest Lead: approve DISPUTE-47 #f6e4
  ```
- **1:18–1:22**: The fest lead (you) types: `approve DISPUTE-47 #f6e4`. Highlight the command with a yellow glow as it's sent. (Use the code your marshal actually generated.)
- **1:22–1:25**: `@techstorm-bracket-marshal` confirms: *"✅ APPROVED: DISPUTE-47. MATCH-47 → rematch_scheduled. 📣 ANNOUNCE @techstorm-concierge"*
- **1:25–1:30**: **Switch back to `#public-helpdesk`**. `@techstorm-concierge` posts:
  ```
  📢 RULING: FIFA 25 MATCH-47 ⚖️
  TikiTaka_Pro vs Mbappe_Rush will be replayed in full (BO1)
  🕕 Day 1 (Dec 14), 20:00 IST, Arena Alpha
  ```

### 🎨 Visual Notes:
- The **cross-room transition** is the money shot — use a smooth animated arrow or channel-switch effect
- Highlight the `approve` command with a pulsing yellow border
- Add a small timer overlay showing elapsed time (aim for ~25–30 seconds for the full flow)
- Use picture-in-picture if possible: show helpdesk in a small window while ops is the main view

---

## [1:30 – 1:50] Why Switch?

### 🎙️ Voiceover:
> "So how does this work under the hood? The whole topology is one YAML file: three rooms, three agents, who can address each agent, and the documents each room holds."
>
> *[Pause while YAML is on screen]*
>
> "Switch scopes who can talk to which agent. Participants can only reach the concierge, and the concierge can only file reports. The agents that change state answer only to me. The money lives in a room the public agent isn't even in."
>
> "Take Switch away and you're back to one all-powerful bot in one channel. FestCommand isn't a bot sitting on top of Switch. Switch draws the boundaries that make it safe."

### 📺 On Screen:
- **1:30–1:35**: Full-screen view of `festcommand.template.yaml`. Slow scroll through the file.
- **1:35–1:40**: Highlight key sections with colored overlays and callout labels:
  - `addressing: { anyone_in: [helpdesk, ops] }` on the concierge → **"Participants reach only this agent"** (green label)
  - `addressing: owner-agents` on marshal & tracker → **"Answers only to the Fest Lead"** (red label)
  - `docs:` on the ops & finance rooms → **"Shared live state"** (blue label)
  - `agents: [bracket_marshal, concierge, sponsor_tracker]` on ops → **"Agents in two rooms carry the hand-offs"** (purple label)
- **1:40–1:45**: Animated diagram: show the 3 rooms with arrows. Highlight each arrow as you mention cross-room features.
- **1:45–1:50**: Quick comparison table (from README) flashes on screen:

  | Without Switch | With FestCommand |
  |---|---|
  | 12 WhatsApp groups | 3 structured rooms |
  | No approval flow | Human gates at every decision |
  | Copy-paste updates | Auto cross-room notifications |

### 🎨 Visual Notes:
- The YAML file should feel like the "source code" of the operation — treat it as a reveal
- Use callout animations (popping labels) to make the YAML readable
- The comparison table should be punchy — only on screen for 3–4 seconds

---

## [1:50 – 2:00] Close

### 🎙️ Voiceover:
> "FestCommand. Three rooms. Three agents. One command center. Because your fest deserves better than a WhatsApp group with 347 unread messages."
>
> "Link in the description. Built for Flip the Switch."

### 📺 On Screen:
- **1:50–1:55**: FestCommand logo, large and centered. Below it:
  ```
  github.com/945040ad/Flip-the-Switch
  ```
- **1:55–2:00**: Badges fade in below:
  - "Built for Flip the Switch 2026"
  - "Track: Best Business Workflow"
  - "Powered by Switch"
- **2:00**: Fade to black.

### 🎨 Visual Notes:
- Clean, minimal closing screen
- The tagline should feel like a mic drop
- Optional: add a QR code linking to the repo

---

## Production Notes

### Recording Setup
- **Screen recording**: OBS Studio or Loom at 1080p
- **Audio**: Record voiceover separately in Audacity for clean audio; mix in post
- **Editing**: DaVinci Resolve (free) or CapCut

### Timing Checkpoints
| Timestamp | Section | Duration |
|---|---|---|
| 0:00 | Hook | 15s |
| 0:15 | What is FestCommand | 15s |
| 0:30 | Demo: Schedule Question | 30s |
| 1:00 | Demo: Dispute + Approval | 30s |
| 1:30 | Why Switch | 20s |
| 1:50 | Close | 10s |
| **Total** | | **2:00** |

### Key Moments to Nail
1. **The chaos montage** (0:00–0:15): Must be relatable. Every fest organizer has lived this.
2. **The cross-room transition** (1:08–1:12): This is the Switch differentiator. Make it visually clear.
3. **The approval command** (1:18–1:22): Human-in-the-loop is the trust builder. Highlight it.
4. **The YAML reveal** (1:30–1:40): Shows this isn't smoke and mirrors — it's a real, reproducible template.

### Assets Needed
- [ ] FestCommand logo (PNG, transparent background)
- [ ] Discord server with FestCommand deployed from the template (run `python scripts/rehearse.py` first to rehearse the exact lines)
- [ ] WhatsApp chaos screenshots (mockup — use placeholder names)
- [ ] Background music (royalty-free, lo-fi or electronic)
- [ ] OBS scene layouts for each section
