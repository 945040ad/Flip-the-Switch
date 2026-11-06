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
- **0:15–0:20**: Switch Console opens. Click **Import Template** → select `festcommand.template.yaml`
- **0:20–0:25**: The YAML file briefly scrolls on screen. Highlight the three room definitions with colored boxes:
  - 🟢 `#public-helpdesk` (green)
  - 🟡 `#tournament-ops` (yellow)
  - 🔴 `#sponsor-finance` (red)
- **0:25–0:30**: Animated transition showing the three Discord channels appearing in the sidebar. Zoom into the channel list.

### 🎨 Visual Notes:
- Use colored labels/boxes overlaid on the YAML to match each room
- Quick zoom transitions between the three channels
- Optional: show the architecture diagram from the README for 2 seconds

---

## [0:30 – 1:00] Live Demo — Schedule Question

### 🎙️ Voiceover:
> "Let's see it in action. A participant drops into the public helpdesk and asks: 'When is the Valorant semifinal?'"
>
> *[2-second pause while the message appears]*
>
> "The concierge agent reads the live schedule document and responds instantly. Match time, map pool, check-in instructions — all accurate, all from a single source of truth that the ops team can update in real time."
>
> "No more 'check the pinned message.' No more 'ask in the other group.'"

### 📺 On Screen:
- **0:30–0:35**: Discord `#public-helpdesk` channel is visible. A user named `@gamer_priya` types: *"When is the Valorant semifinal?"*
- **0:35–0:42**: `@concierge-agent` responds with a formatted message:
  ```
  🎮 Valorant Semifinal — Day 2
  📅 Sunday, March 15 | 2:00 PM IST
  📍 Main Stage (Hall A)
  🗺️ Map Pool: Ascent, Bind, Haven (Bo3)
  ⏰ Check-in opens at 1:30 PM

  Good luck! 🔥
  ```
- **0:42–0:50**: Quick side-by-side showing `schedule_and_rules.md` in the Switch document panel alongside the Discord response. Draw a line connecting the source to the answer.
- **0:50–1:00**: Zoom out to show the full channel. Another participant asks a different question; the concierge handles it.

### 🎨 Visual Notes:
- Use a subtle green glow/highlight on the agent's response to draw attention
- The side-by-side with the source document is key — shows it's reading from a live doc, not hallucinating
- Keep the pace brisk here — this is the simple scenario

---

## [1:00 – 1:30] Live Demo — Match Dispute + Human Approval

### 🎙️ Voiceover:
> "Now watch the real magic. A player reports cheating in the public helpdesk."
>
> *[Brief pause]*
>
> "The concierge doesn't try to resolve it — it formats a structured dispute report and escalates to tournament ops, a restricted room that participants can't access."
>
> "The bracket marshal checks the roster in the bracket state file, finds a violation, and asks ME for approval. Watch."
>
> *[Pause as approval appears]*
>
> "I type 'approve DISPUTE-05 #c4d1'. That hash is a verification code. One command."
>
> "The bracket updates. And back in the helpdesk — the concierge announces the ruling. Two rooms, two agents, one human gate, thirty seconds."

### 📺 On Screen:
- **1:00–1:05**: In `#public-helpdesk`, user `@rage_quit_ravi` types: *"TeamGamma used a player not on their roster in MATCH-09. This is cheating."*
- **1:05–1:08**: `@concierge-agent` responds:
  ```
  ⚖️ Dispute Report Filed
  📋 ID: DISPUTE-05
  🎮 Match: MATCH-09 (BGMI Squad)
  📝 Category: Roster violation
  ⬆️ Escalating to tournament ops...
  ```
- **1:08–1:12**: **Transition animation**: A message arrow flies from `#public-helpdesk` to `#tournament-ops`. Switch to the `#tournament-ops` channel view.
- **1:12–1:18**: In `#tournament-ops`, `@bracket-marshal` posts:
  ```
  ⚖️ DISPUTE-05 Investigation
  Match: MATCH-09 | TeamGamma vs TeamDelta
  Finding: Player "ShadowX" is NOT on TeamGamma's registered roster.
  Rule: Section 4.2 — All players must be registered 24h before match.
  Recommendation: TeamGamma forfeits MATCH-09. TeamDelta advances.

  🔒 Requires approval: approve DISPUTE-05 #c4d1
  ```
- **1:18–1:22**: The fest lead (you) types: `approve DISPUTE-05 #c4d1`. Highlight the command with a yellow glow as it's sent.
- **1:22–1:25**: `@bracket-marshal` confirms: *"✅ DISPUTE-05 approved. Bracket updated. Notifying helpdesk..."*
- **1:25–1:30**: **Switch back to `#public-helpdesk`**. `@concierge-agent` posts:
  ```
  📢 Dispute Resolution — DISPUTE-05
  ⚖️ Ruling: TeamGamma forfeits MATCH-09 (roster violation).
  ➡️ TeamDelta advances to the quarterfinal.
  ```

### 🎨 Visual Notes:
- The **cross-room transition** is the money shot — use a smooth animated arrow or channel-switch effect
- Highlight the `approve` command with a pulsing yellow border
- Add a small timer overlay showing elapsed time (aim for ~25–30 seconds for the full flow)
- Use picture-in-picture if possible: show helpdesk in a small window while ops is the main view

---

## [1:30 – 1:50] Why Switch?

### 🎙️ Voiceover:
> "So how does this all work under the hood? This entire topology — three rooms, three agents, addressing policies, shared documents, cross-room links — is defined in one YAML file."
>
> *[Pause while YAML is on screen]*
>
> "Switch handles the routing. It scopes who can talk to which agent. It shares documents across rooms so every agent sees the same bracket state. And it enforces human approval gates."
>
> "Take Switch away, and none of this works. You can't do cross-room escalation. You can't scope agent access. You can't share live documents. FestCommand isn't a bot sitting on top of Switch — Switch IS the infrastructure."

### 📺 On Screen:
- **1:30–1:35**: Full-screen view of `festcommand.template.yaml`. Slow scroll through the file.
- **1:35–1:40**: Highlight key sections with colored overlays and callout labels:
  - `addressing: anyone` → **"Open to all participants"** (green label)
  - `addressing: owner-agents` → **"Restricted to fest lead + agents"** (red label)
  - `documents:` section → **"Shared live state"** (blue label)
  - `group-links:` section → **"Cross-room routing"** (purple label)
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
  github.com/YOUR_USERNAME/festcommand
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
- [ ] Discord server with 3 channels set up (or convincing mockup)
- [ ] WhatsApp chaos screenshots (mockup — use placeholder names)
- [ ] Background music (royalty-free, lo-fi or electronic)
- [ ] OBS scene layouts for each section
