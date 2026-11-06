#!/usr/bin/env python3
"""
FestCommand Rehearsal Script
============================
Simulates the full multi-agent workflow in ~60 seconds.
Run: python scripts/rehearse.py

This script demonstrates the FestCommand workflow WITHOUT requiring
a running Switch instance. It walks through a realistic scenario
showing how the three agents and three rooms interact.
"""

import json
import time
import random
import string
import sys
from pathlib import Path
from datetime import datetime

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def gen_hash():
    return '#' + ''.join(random.choices(string.hexdigits[:16], k=4))

def print_room(room_name, color):
    print(f"\n{color}{Colors.BOLD}{'='*60}")
    print(f"  📍 Room: {room_name}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_message(sender, message, color=Colors.RESET, delay=0.8):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"  {Colors.DIM}[{timestamp}]{Colors.RESET} {color}{Colors.BOLD}{sender}{Colors.RESET}")
    for line in message.split('\n'):
        print(f"    {line}")
    print()
    time.sleep(delay)

def print_divider(text=""):
    if text:
        print(f"\n{Colors.DIM}{'─'*20} {text} {'─'*20}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.DIM}{'─'*60}{Colors.RESET}\n")

def load_documents():
    docs_dir = Path(__file__).parent.parent / "documents"
    bracket = json.loads((docs_dir / "bracket_state.json").read_text(encoding="utf-8"))
    ledger = json.loads((docs_dir / "sponsor_ledger.json").read_text(encoding="utf-8"))
    return bracket, ledger

def main():
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         🎮 FestCommand Rehearsal Simulation 🎮          ║")
    print("║       Multi-Room Esports & Event Ops War Room           ║")
    print("║                  TechStorm 2026                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"{Colors.DIM}Loading event documents...{Colors.RESET}")
    try:
        bracket, ledger = load_documents()
        print(f"{Colors.GREEN}✓ Loaded bracket_state.json ({len(bracket.get('tournaments', {}))} tournaments){Colors.RESET}")
        print(f"{Colors.GREEN}✓ Loaded sponsor_ledger.json ({len(ledger.get('sponsors', []))} sponsors){Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ Could not load documents: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}  (Running with simulated data){Colors.RESET}")
        bracket, ledger = {}, {}
    
    time.sleep(1)
    
    # ══════════════════════════════════════════════
    # SCENARIO 1: Participant asks about schedule
    # ══════════════════════════════════════════════
    print_divider("SCENARIO 1: Schedule Question")
    print_room("#techstorm-public-helpdesk", Colors.CYAN)
    
    print_message("👤 Participant (Rahul)", 
                  "Hey @techstorm-concierge when is the Valorant semifinal? My team Phoenix Esports qualified!", 
                  Colors.BLUE)
    
    print_message("🤖 @techstorm-concierge",
                  "Hey Rahul! Congrats on making it to the semis! 🏆\n\n"
                  "📅 **Valorant Semifinals**\n"
                  "• **Date**: December 15, 2026 (Day 2)\n"
                  "• **Time**: 10:00 AM — 12:30 PM\n"
                  "• **Stage**: Arena Alpha\n"
                  "• **Format**: Best of 3 (BO3)\n\n"
                  "Your match: **MATCH-09** — Phoenix Esports vs TBD (winner of QF-4)\n\n"
                  "Make sure your full 5-player roster checks in at the Arena Alpha desk\n"
                  "15 minutes before match time. GL HF! 🎮",
                  Colors.GREEN)
    
    # ══════════════════════════════════════════════
    # SCENARIO 2: Match result + approval flow
    # ══════════════════════════════════════════════
    print_divider("SCENARIO 2: Match Result Validation & Approval")
    print_room("#techstorm-public-helpdesk", Colors.CYAN)
    
    print_message("👤 Match Referee",
                  "@techstorm-concierge Match MATCH-07 just finished.\n"
                  "Team Mayhem beat Clutch Gaming 13-9 on Ascent.\n"
                  "Screenshot: https://imgur.com/val-match07-proof",
                  Colors.BLUE)
    
    print_message("🤖 @techstorm-concierge",
                  "Got it! 📋 Forwarding the match result to our tournament ops team for validation.\n\n"
                  "You'll see the updated bracket shortly once it's verified. Thanks, ref!",
                  Colors.GREEN)
    
    time.sleep(0.5)
    print_room("#techstorm-tournament-ops", Colors.YELLOW)
    
    hash1 = gen_hash()
    print_message("🤖 @techstorm-concierge → @techstorm-bracket-marshal",
                  "📋 **MATCH RESULT SUBMISSION**\n"
                  "Match: MATCH-07\n"
                  "Game: Valorant — Quarterfinal 3\n"
                  "Teams: Team Mayhem vs Clutch Gaming\n"
                  "Result: Team Mayhem wins 13-9 (Ascent)\n"
                  "Proof: https://imgur.com/val-match07-proof\n"
                  "Source: Match Referee via #public-helpdesk",
                  Colors.GREEN)
    
    print_message("🤖 @techstorm-bracket-marshal",
                  f"Validating MATCH-07...\n\n"
                  f"✓ Match ID MATCH-07 exists in bracket — Valorant QF-3\n"
                  f"✓ Teams confirmed: Team Mayhem vs Clutch Gaming\n"
                  f"✓ Score format valid: 13-9 (within 13-round Valorant range)\n"
                  f"✓ Screenshot proof provided\n\n"
                  f"✅ **MATCH RESULT — READY FOR APPROVAL**\n"
                  f"Match: MATCH-07\n"
                  f"Game: Valorant — Quarterfinal 3\n"
                  f"Winner: Team Mayhem\n"
                  f"Score: 13-9 (Ascent)\n"
                  f"Proof: https://imgur.com/val-match07-proof\n\n"
                  f"Fest Lead: `approve MATCH-07 {hash1}`",
                  Colors.YELLOW)
    
    time.sleep(1.5)
    print_message("👑 Fest Lead (Priya)",
                  f"approve MATCH-07 {hash1}",
                  Colors.RED)
    
    print_message("🤖 @techstorm-bracket-marshal",
                  f"✅ **APPROVED** — MATCH-07 {hash1}\n"
                  f"• bracket_state.json updated: Team Mayhem advances to SF-2\n"
                  f"• Downstream: MATCH-10 (Semifinal 2) now set: Phoenix Esports vs Team Mayhem\n"
                  f"• Notifying @techstorm-concierge to announce in #public-helpdesk",
                  Colors.YELLOW)
    
    time.sleep(0.5)
    print_room("#techstorm-public-helpdesk", Colors.CYAN)
    
    print_message("🤖 @techstorm-concierge",
                  "📢 **BRACKET UPDATE — VALORANT** ⚔️\n\n"
                  "**Quarterfinal 3 Result**: Team Mayhem 🏆 defeats Clutch Gaming (13-9, Ascent)\n\n"
                  "**Updated Semifinal 2**: Phoenix Esports vs Team Mayhem\n"
                  "📅 Tomorrow at 10:00 AM, Arena Alpha\n\n"
                  "The bracket is heating up! Who's your pick for the semis? 🔥",
                  Colors.GREEN)
    
    # ══════════════════════════════════════════════
    # SCENARIO 3: Dispute escalation
    # ══════════════════════════════════════════════
    print_divider("SCENARIO 3: Match Dispute & Resolution")
    print_room("#techstorm-public-helpdesk", Colors.CYAN)
    
    print_message("👤 Participant (Vikram, Captain of NoScope Legends)",
                  "@techstorm-concierge I want to file a dispute for MATCH-05.\n"
                  "The other team (Hydra Officials) had a player disconnect mid-round\n"
                  "and they subbed in a ringer who wasn't on their original roster.\n"
                  "I have screenshots: https://imgur.com/dispute-match05-roster",
                  Colors.BLUE)
    
    print_message("🤖 @techstorm-concierge",
                  "I hear you, Vikram. Roster violations are taken seriously. 📋\n\n"
                  "I'm escalating this to our tournament ops team right now with\n"
                  "all the details. You'll hear back within 15 minutes.\n\n"
                  "Hang tight — we've got your back. ⚔️",
                  Colors.GREEN)
    
    time.sleep(0.5)
    print_room("#techstorm-tournament-ops", Colors.YELLOW)
    
    print_message("🤖 @techstorm-concierge → @techstorm-bracket-marshal",
                  "🚨 **DISPUTE REPORT**\n"
                  "Match: MATCH-05\n"
                  "Game: Valorant — Quarterfinal 1\n"
                  "Teams: NoScope Legends vs Hydra Officials\n"
                  "Issue: Unauthorized player substitution — Hydra Officials allegedly\n"
                  "       swapped in an unregistered player after a disconnect\n"
                  "Evidence: https://imgur.com/dispute-match05-roster\n"
                  "Reporter: Vikram (Captain, NoScope Legends)\n"
                  "Timestamp: 2026-12-14 14:32 IST",
                  Colors.GREEN)
    
    hash2 = gen_hash()
    print_message("🤖 @techstorm-bracket-marshal",
                  f"Investigating MATCH-05 dispute...\n\n"
                  f"📋 **Analysis**:\n"
                  f"• Checked registered roster for Hydra Officials: 5 players + 1 sub\n"
                  f"• Screenshot shows player 'xHydra_Nova' in-game — NOT on registered roster or sub list\n"
                  f"• Rule 4.3: 'Only registered roster members and declared substitutes may play'\n"
                  f"• Rule 4.5: 'Unauthorized substitution results in match forfeiture'\n\n"
                  f"⚖️ **DISPUTE RESOLUTION — MATCH-05**\n"
                  f"Finding: Roster violation confirmed — unregistered player used\n"
                  f"Recommendation: **Forfeit** — Hydra Officials forfeit MATCH-05\n"
                  f"Impact: NoScope Legends advance to Semifinal 1 (MATCH-09)\n"
                  f"        MATCH-09 becomes: NoScope Legends vs Shadow Strikers\n\n"
                  f"Fest Lead: `approve DISPUTE-05 {hash2}`",
                  Colors.YELLOW)
    
    time.sleep(1.5)
    print_message("👑 Fest Lead (Priya)",
                  f"approve DISPUTE-05 {hash2}",
                  Colors.RED)
    
    print_message("🤖 @techstorm-bracket-marshal",
                  f"✅ **APPROVED** — DISPUTE-05 {hash2}\n"
                  f"• Hydra Officials disqualified from MATCH-05\n"
                  f"• NoScope Legends advance to SF-1 (MATCH-09)\n"
                  f"• bracket_state.json updated\n"
                  f"• Notifying @techstorm-concierge",
                  Colors.YELLOW)
    
    time.sleep(0.5)
    print_room("#techstorm-public-helpdesk", Colors.CYAN)
    
    print_message("🤖 @techstorm-concierge",
                  "📢 **DISPUTE RESOLVED — MATCH-05** ⚖️\n\n"
                  "After reviewing evidence, the tournament ops team has ruled:\n"
                  "• **Hydra Officials** — disqualified from QF-1 (roster violation)\n"
                  "• **NoScope Legends** — advance to Semifinal 1 🏆\n\n"
                  "Updated bracket:\n"
                  "**SF-1 (MATCH-09)**: NoScope Legends vs Shadow Strikers\n"
                  "📅 Tomorrow 10:00 AM, Arena Alpha\n\n"
                  "Fair play keeps the tournament strong. GG to all teams. ⚔️",
                  Colors.GREEN)
    
    # ══════════════════════════════════════════════
    # SCENARIO 4: Prize payout
    # ══════════════════════════════════════════════
    print_divider("SCENARIO 4: Prize Payout & Sponsor Finance")
    print_room("#techstorm-tournament-ops", Colors.YELLOW)
    
    print_message("🤖 @techstorm-bracket-marshal",
                  "🏆 **TOURNAMENT COMPLETE — BGMI**\n\n"
                  "Final standings after 3 rounds:\n"
                  "🥇 1st: Starter Pack (487 pts)\n"
                  "🥈 2nd: JERC Esports (445 pts)\n"
                  "🥉 3rd: Rush Gamers (412 pts)\n\n"
                  "@techstorm-sponsor-tracker please initiate prize payouts",
                  Colors.YELLOW)
    
    time.sleep(0.5)
    print_room("#techstorm-sponsor-finance", Colors.RED)
    
    hash3 = gen_hash()
    hash4 = gen_hash()
    hash5 = gen_hash()
    print_message("🤖 @techstorm-sponsor-tracker",
                  f"💰 **PAYOUT REQUEST — BGMI Prize Pool**\n\n"
                  f"Funded by: Monster Energy (Gold Sponsor)\n\n"
                  f"💰 PAYOUT-01\n"
                  f"  Recipient: Starter Pack (1st place)\n"
                  f"  Amount: ₹40,000\n"
                  f"  Fest Lead: `approve PAYOUT-01 {hash3}`\n\n"
                  f"💰 PAYOUT-02\n"
                  f"  Recipient: JERC Esports (2nd place)\n"
                  f"  Amount: ₹20,000\n"
                  f"  Fest Lead: `approve PAYOUT-02 {hash4}`\n\n"
                  f"💰 PAYOUT-03\n"
                  f"  Recipient: Rush Gamers (3rd place)\n"
                  f"  Amount: ₹10,000\n"
                  f"  Fest Lead: `approve PAYOUT-03 {hash5}`\n\n"
                  f"📊 **Budget Status**: BGMI prize pool ₹70,000 / ₹70,000 allocated (100%)\n"
                  f"⚠️ This will fully exhaust the BGMI prize allocation.",
                  Colors.RED)
    
    time.sleep(1.5)
    print_message("👑 Fest Lead (Priya)",
                  f"approve PAYOUT-01 {hash3}",
                  Colors.BLUE)
    
    print_message("🤖 @techstorm-sponsor-tracker",
                  f"✅ PAYOUT-01 approved — ₹40,000 to Starter Pack\n"
                  f"• sponsor_ledger.json updated\n"
                  f"• Remaining BGMI pool: ₹30,000",
                  Colors.RED)
    
    # ══════════════════════════════════════════════
    # SCENARIO 5: Sponsor status check
    # ══════════════════════════════════════════════
    print_divider("SCENARIO 5: Sponsor Deliverable Check")
    print_room("#techstorm-sponsor-finance", Colors.RED)
    
    print_message("👑 Fest Lead (Priya)",
                  "@techstorm-sponsor-tracker give me a sponsor status update",
                  Colors.BLUE)
    
    sponsor_table = (
        "📊 **SPONSOR STATUS — Dec 14, 2026**\n\n"
        "| Sponsor        | Tier         | Booth | Banner | Swag  | Social | Stage |\n"
        "|----------------|------------- |-------|--------|-------|--------|-------|\n"
        "| HyperX         | 🏆 Title    | ✅    | ✅     | ✅    | ✅     | ⏳ 1/2 |\n"
        "| Monster Energy | 🥇 Gold     | ✅    | ⏳     | ✅    | ❌ 0/2 | ✅     |\n"
        "| Logitech       | 🥇 Gold     | ✅    | ✅     | ⏳    | ✅     | ✅     |\n"
        "| AMD            | 🥈 Silver   | ✅    | ✅     | N/A   | ⏳ 1/2 | N/A   |\n"
        "| Jio            | 🤝 Partner  | N/A   | ✅     | ✅    | ✅     | N/A   |\n\n"
        "⚠️ **Action Required**:\n"
        "• Monster Energy: 0/2 social media posts completed — deadline is tonight\n"
        "• Logitech: Swag bag items (mousepads) still in transit — ETA 3 PM today\n"
        "• HyperX: Day 2 stage shoutout (Valorant Finals) still pending"
    )
    
    print_message("🤖 @techstorm-sponsor-tracker", sponsor_table, Colors.RED)
    
    # ══════════════════════════════════════════════
    # WRAP UP
    # ══════════════════════════════════════════════
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║              ✅ Rehearsal Complete!                      ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Scenarios demonstrated:                                ║")
    print("║  1. 📅 Schedule question (helpdesk → document lookup)   ║")
    print("║  2. ✅ Match validation (helpdesk → ops → approval)     ║")
    print("║  3. ⚖️  Dispute resolution (helpdesk → ops → approval)  ║")
    print("║  4. 💰 Prize payout (ops → finance → approval)          ║")
    print("║  5. 📊 Sponsor status check (finance → ledger query)    ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Rooms used: 3  |  Agents used: 3  |  Approvals: 4     ║")
    print("║  Cross-room handoffs: 5  |  Documents queried: 3       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"{Colors.DIM}To deploy this workflow on Switch:{Colors.RESET}")
    print(f"  1. Import festcommand.template.yaml into Switch Console")
    print(f"  2. Set your fest name parameter (default: 'techstorm')")
    print(f"  3. Choose your chat platform bridge (Discord/Slack/Mattermost)")
    print(f"  4. Upload documents/ to the created rooms")
    print(f"  5. Start chatting! 🎮\n")

if __name__ == "__main__":
    main()
