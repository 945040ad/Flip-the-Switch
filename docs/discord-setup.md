# Run FestCommand on Discord

About 15 minutes from nothing to three agents working in your Discord server.
Everything runs on your own computer: Switch connects out to Discord, so
nothing has to be reachable from the internet.

You need:

- A Discord server you can add a bot to. Make a fresh one for the event.
- A coding agent signed in on this computer: Claude Code, Codex or OpenCode.
  FestCommand's agents run as its sessions.

## 1. Create the Discord bot

1. In the [Discord Developer Portal](https://discord.com/developers/applications),
   choose **New Application** and name it (e.g. *FestCommand*).
2. Open the **Bot** tab:
   - **Reset Token**, then copy the token straight into your password manager.
     It is the only secret in this guide. The *Application ID* and *Public
     Key* on the General Information page are **not** the token.
   - Under **Privileged Gateway Intents**, turn on **Server Members Intent**
     and **Message Content Intent**, then **Save Changes**.
3. Invite the bot. Replace `APP_ID` with your Application ID and open:

   ```
   https://discord.com/oauth2/authorize?client_id=APP_ID&scope=bot+applications.commands&permissions=275683314704
   ```

   The scopes let Switch publish its slash commands. The permission number
   grants exactly what Switch needs: View Channels, Send Messages, Send
   Messages in Threads, Manage Webhooks (agents post under their own names),
   Manage Channels and Manage Roles (FestCommand's private rooms), Read Message
   History and Attach Files.
4. In Discord, turn on **User Settings → Advanced → Developer Mode**,
   right-click your server's icon and **Copy Server ID**.

## 2. Start Switch with Switch Console

1. Install [Switch Console](https://github.com/sandbox-quantum/switch#get-started-in-two-steps)
   ([Windows installer](https://github.com/sandbox-quantum/switch/releases/latest/download/switch-console-x64.exe)).
2. **Add a server → Run a server on this computer.** No Docker needed. The
   first start takes a minute or two while it prepares its own Python and
   PostgreSQL. "Waiting for the server to become healthy" during that time is
   normal.
3. **Agent providers**: choose your coding agent and sign in.

## 3. Connect Discord

On the server's **Home** page: **Messaging apps → Connect → Discord**.

- **Name**: anything, e.g. *TechStorm Discord*. You pick it by this name later.
- **Bot Token** and **Guild Id**: from step 1.

Then link your Discord account (**This is me**). The bracket marshal and the
sponsor tracker answer only their owner, so they can't recognise your
`approve` lines until this is done.

## 4. Deploy FestCommand

**Templates → Import** `festcommand.template.yaml`, then fill in:

| Field | Value |
|---|---|
| Fest display name | `TechStorm 2026` (or your fest) |
| Fest short name | `techstorm` |
| Messaging app | **the Discord connection you just made** |

Set the messaging app explicitly. A Switch Console server usually also runs
its built-in Mattermost, and the field otherwise defaults to the first
messaging app on the server.

**Create.** Switch creates the three agents on your computer, then three
Discord channels with their documents:

| Channel | Who's in it |
|---|---|
| `#techstorm-public-helpdesk` | everyone, plus the concierge |
| `#techstorm-tournament-ops` | private: you, marshal, concierge, tracker |
| `#techstorm-sponsor-finance` | private: you and the tracker |

Each agent's kickoff takes one to two minutes. It ends with every stateful
agent owning its live copy of the documents. Confirm it from a terminal:

```bash
python scripts/live_check.py inspect --console
```

It checks that `bracket_live_<game>.json` ×4 and `approvals_live.json` were
created by the marshal, `ledger_live.json` by the tracker and
`announcements.md` by the concierge, and that each copy matches the template.

## 5. Try it

In `#techstorm-public-helpdesk` (ideally from a second account, as a
participant):

> @techstorm-concierge we won our semi!! when and where is the Valorant final?

> @techstorm-concierge dispute on MATCH-47! Opponent disconnected at 1-1 in
> 85th minute, claims server lag. I had possession in the attacking third.

The marshal posts its ruling proposal in `#techstorm-tournament-ops`, ending
with an approval line. Approve it from your own account with the code it gives:

> @techstorm-bracket-marshal approve DISPUTE-47 #xxxx

The concierge then announces the ruling in the helpdesk. Agents are real
coding-agent sessions, so each reply takes 10 to 60 seconds.
[demo/video-script.md](../demo/video-script.md) has the full scene list.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Messaging app shows *bridge is not running*; the server log says `401 Unauthorized`, `Improper token has been passed` | The token is wrong: Application ID or Public Key pasted instead, or the token was reset after copying. **Bot → Reset Token**, paste the new one into the connection. |
| Bot is online but agents never see messages | **Message Content Intent** is off. Turn it on and **Save Changes**. |
| No `/` commands in Discord | The bot was invited without the `applications.commands` scope. Re-invite with the link above. |
| The marshal or tracker ignores you | Your Discord account isn't linked: **Home → Messaging apps → Link → This is me**. |
| Channels appeared in Mattermost instead | The *Messaging app* field was left on its default. Delete the three rooms and the three `techstorm-*` agents, then deploy again with Discord selected. |
| Log shows `Could not post the activity … Discord has no thread` | Switch's "agent is working" indicator, not FestCommand. Harmless. |

The Switch Console server's log is in
`%APPDATA%\switchdash\local-switch-server\native\logs\switch-core.log`
(Windows).
