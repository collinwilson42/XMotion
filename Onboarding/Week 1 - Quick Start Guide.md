---
name: XMotion Quick Start
description: Week 1 workstation setup and Airbnb sourcing/scoring workflow for new XMotion virtual assistants. Covers installs, Windows MCP, XCopy capture tool, Obsidian vault, Outlook, two‑loop property evaluation, and Claude‑guided scoring. Non‑technical audience — every step runs through Claude.
tools: windows-mcp, filesystem, memory, sequential-thinking, claude-mem, find-skills, superpowers, impeccable, task-observer
type: onboarding
domain: va-training
status: live
version: 1.2
updated: 2026-07-10
audience: XMotion VAs (Jaisa & Richlan)
maintainer: XMotion
signed: Collin 
growth:
  - Add video generation loop once Higgsfield integration is stable
  - Build automated S‑value rotation and conversion tracking per the analytics pipeline
  - Roll Power-Ups (Part 9) from optional to standard once claude-mem stability is confirmed on VA machines
---

# XMotion — Week 1 Quick Start Guide


Here's the one thing to know before you start: **you do not need to be technical.** Your main tool is Claude, an AI assistant that can actually control your computer, set up software, and do the heavy lifting for you. Most of this guide is literally *copying a message, pasting it to Claude, and letting it work.* If something doesn't make sense, ask Claude — that's the whole point.

This week has one job: **get your workstation set up so you can start producing.** Take it one part at a time. There's no rush, and nothing here can break your computer.

Let's go.

— Collin

---

## What you’re setting up this week

There are nine pieces to your workstation, and they build on each other. By the end, you’ll have an AI assistant that can run your machine, a capture pipeline that grabs listing photos, and a scoring system that tells you if a property is ready to turn into a video. Everything below is done _with_ Claude, not instead of it — you’ll copy prompts and let the AI do the heavy lifting.

1. **Install the core apps**  
    A one-command install of Claude, Obsidian, Alacritty, Node.js, Python, Git, and PowerToys. These are the only programs your machine needs for the whole XMotion workflow — nothing else to hunt down.
    
2. **Set up your XMotion Outlook inbox**  
    Everyone on the team uses the same shared inbox (`inbox.xmotion@outlook.com`) for customer outreach. You’ll sign in once so you’re ready when we start contacting listing owners.
    
3. **Sign in to your XMotion Claude account**  
    The Claude desktop app is your main tool. You’ll log in with the team account so you have access to the paid features, longer context, and the shared project skills we’ve built.
    
4. **Your first mission — teach Claude to control your computer (Windows MCP)**  
    This is the keystone. You’ll install a “Windows MCP server” that lets Claude create folders, edit files, and run commands on your PC. Once that’s working, almost every other setup step can be done by pasting a sentence into chat. You’ll also add two helper servers (memory and sequential-thinking) that make Claude smarter over time.
    
5. **Create your work folder and load the XMotion files**  
    Using Claude’s new ability to control your PC, you’ll make a `C:\dev` folder and place the whole XMotion project inside it — capture tool, AI skill files, onboarding guides, and your future captures. This folder becomes the single home base for everything you produce.
    
6. **Set up Obsidian Vault**  
    Obsidian is where you’ll read the onboarding guides and keep your own notes. You’ll point it at the `C:\dev\XMotion` folder so the skill files, capture logs, and checklists all live in one searchable, linked notebook. (You’ll come back to this after Part 4 because the folder needs to exist first.)
    
7. **A fun demo to see what Claude can do**  
    In one chat, you’ll ask Claude to design a color palette and apply it to a terminal window by editing a config file — something that normally feels very technical. This shows you the pattern for the rest of the setup: you describe the outcome, Claude writes the changes. You’ll also test the capture tool (XCopy) for the first time by copying a few Airbnb listing images and watching them organize themselves.
    
8. **Install the capture tool and take your first shots**  
    The XCopy tool is how you grab listing photos at full resolution into timestamped folders. You’ll run it from the terminal, confirm it works, then practice on a real Airbnb property — choosing one with strong walkthrough potential. This is the first real production step, and it feeds directly into the scoring system.
    
9. **Give Claude access to your work folder**  
    Finally, you’ll add a filesystem MCP server so Claude can read the captured images and the project files directly. That means you’ll be able to say “grade the thumbnails in today’s capture block” and Claude will do it without you uploading anything. That’s the bridge from setup into real work.
    

Take them one at a time, in order. If anything feels off, ask Claude.


---

## Part 1 — Install the core apps

Open the **Start menu**, type `cmd`, and open **Command Prompt**. Copy the block below, right-click to paste, and press Enter. This installs everything at once (say "Yes" to any prompts).

```
winget install -e --id Anthropic.Claude
winget install -e --id Obsidian.Obsidian
winget install -e --id Alacritty.Alacritty
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Python.Python.3.13
winget install -e --id Git.Git
winget install --id Microsoft.PowerToys
```

What each one is:
- **Claude** — your AI assistant and main tool. [claude.ai/download](https://claude.ai/download)
- **Obsidian** — where you'll read guides like this one and log your work. [obsidian.md/download](https://obsidian.md/download)
- **Alacritty** — a terminal window (we'll customize it in a fun way in Part 5). [alacritty.org](https://alacritty.org)
- **Node.js** — runs behind the scenes so Claude's tools work. (No window opens — that's normal.)
- **Python** —  (Also no window — normal.)
- **Git** — will use later for refreshing the obsidian vault or an automatic sync
- **Power Toys** — priority layout mode
- **Outlook (new)** — free Microsoft Store client for the shared team inbox used for customer outreach

If a link is easier than the command for any app, use the link — same result.

**After it finishes, close Command Prompt and open a fresh one** (so the new installs are recognized).

---
## Part 2 — Accounts

### Part 2.1 — Sign in to Outlook

*(single source of truth - we will all use the same email address for customer outreach for now)*
##### Outlook: inbox.xmotion@outlook.com

##### Password: (sent to you directly by Collin)

##### Sign-in PIN: (sent to you directly by Collin)

### Part 2.2 — Sign in to Claude

Open **Claude** (Start menu → type "Claude"). Sign in with the **XMotion company account**:

- Email: `inbox.xmotion@outlook.com` Password: (sent to you directly by Collin)

> Note: Use Outlook to verify login.

### Part 2.3 — Open Obsidian Vault 

> Note: No Sign In - **Return after Part 4
> 
> In Obsidian look for Open Folder as Vault: "c:\dev\XMotion"

---

## Part 3 — Your first mission: teach Claude to control your computer

You're going to have Claude set itself up to control your Windows PC. This is called **Windows MCP**, and once it's on, Claude can create folders, edit files, and run programs *for* you.

Claude will walk you through installing **windows-mcp** and hand you the config. Follow its steps — it may ask you to run one install command. That's expected.

**Step 3.2 — Open the config file.** In Claude, click your **name/profile at the bottom-left → Settings**.

Then go to **Developer** (bottom-left of Settings) and click **Edit Config**.

That opens the folder holding a file called **`claude_desktop_config.json`**. Open it in Notepad (right-click → Open with → Notepad).


**Step 3.3 — Paste the servers.** Use what Claude gave you. If you want a known-good reference, it should look like this (replace `YOUR-USERNAME` with your Windows username — Claude can tell you what it is):

```json
{
  "mcpServers": {
    "windows-mcp": {
      "command": "C:\\Users\\YOUR-USERNAME\\.local\\bin\\windows-mcp.exe",
      "args": [],
      "timeout": 120000
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "timeout": 60000
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "timeout": 60000
    }
  }
}
```

Save the file (Ctrl+S).

**Step 3.4 — Restart Claude.** This is important — Claude only loads new tools on restart. Click the **menu in the very top-left corner → File → Exit** (fully quits it), then open Claude again.

To confirm it worked: start a new chat and ask *"Can you access windows mcp?"* 

---

## Part 4 — Create your work folder and load the XMotion files

Now that Claude can control your PC, let it build your workspace. In a new chat, paste:

> *Using windows-mcp, please create the folder `C:\dev` on my computer.*

Once it's created, download the XMotion project files and put them inside:

- **XMotion Tools and Filebase:** https://github.com/collinwilson42/XMotion

The goal is for the files to end up at **`C:\dev\XMotion`** (so you'll have `C:\dev\XMotion\_Tools`, `C:\dev\XMotion\AI Skills`, and so on). Download the zip to your downloads then request claude unzip it and move it to the dev folder. 

Manual Task: Open the zip folder and copy the XMotion folder. Then go to your file explorer and in the search bar type C:\dev. If claude already created it with windows mcp it should open the workspace folder. Paste in the whole XMotion folder, not the zip but the folder one level within the .zip. 

Prompt: "Using windows-mcp, check my C:\dev folder. I just extracted XMotion.zip here. Confirm the path reads exactly C:\dev\XMotion with the project files (_Tools, AI Skills, Onboarding, Captures) directly inside it — not nested inside a second folder like C:\dev\XMotion\XMotion. If it's nested please fix it. Once it's confirmed correct, give me a brief overview of what's in the folder — the key files and what each part is for — so I understand my workspace and can ask you questions about it."

**(Return to Part 2.3)**

---

## Part 5 — See what Claude can do (the fun one)

Let's prove the power of the **Artifact** and **Windows MCP**: You installed Alacritty (a terminal). Ask Claude to restyle it and create a react artifact — paste this:

### Artifact
Prompt 1: What hex colors would look good transparent background. Can you create a coherent color pallet with (#99FF99) as the primary and (#5f9EA0) as the secondary text for an alacrity toml config. Also, can you create a simple but abstract react artifact using the chosen colors on a glassmorphic background as if it were the alacrity panel."



### Windows MCP 
Prompt 2: *Using windows-mcp, please edit my Alacritty config file (`alacritty.toml`, usually in `%APPDATA%\alacritty\`). Set the window opacity to `0.33` and the hex codes the same as the artifact.

Open Alacritty afterward — you should see the custom layout design. You just edited a system config file without touching a line of code yourself. That's the workflow for everything from here.

### XCopy (Automation Tool)

The capture tool (**XCopy**) grabs listing photos into organized folders. Open alacrity, paste this command line in with ctrl + shift + v

cd C:\dev\XMotion\_Tools
py -m pip install pillow
py XCopy.py -5


- Line 1 moves into the tools folder.
- Line 2 installs `pillow` (an image library the tool needs).
- Line 3 launches XCopy with a 5 minute capture window.

If anything errors, copy the red text, paste it to Claude, and ask it to fix it. (The full capture how-to is in `Onboarding/03_Capture_Guide.md` — this is just to confirm the tool runs.)

What this program does: This is where automation meets productivity. This app allows you to copy images and save them at full resolution to a capture window block, as soon as you copy an image you will see new folders appear in your workspace. example C:\dev\XMotion\Captures\2026-06-30\AM_9-38_9-43\TN_AM_9-38_9-43. The "-5" in py XCopy.py -5 allows you to change the window block for how long you have to capture all the images from a listing before it moves on the next block (for the next listing).

Test it out: We will be starting with Air BNB properties so head over to airbnb.com and think intelligently about finding a property that is for one trending, but most importantly the images give the ai a solid foundation on how the rooms connect and overall it just fits our brand identity as one of the higher end properties on airbnb. **Important note** Before you copy and images make sure you click on the image to expand it to full size and you the right arrow to swiftly copy each image individually once you've settled on the right property.

## Part 7 — Give Claude access to your work folder

Now we give Claude the ability to read and score the property images you've selected, so it can give you feedback before our first video-generation session together.
The tool is called filesystem. Open your config (Settings → Developer → Edit Config → Open JSON, like Part 3), select all (Ctrl+A), copy it (Ctrl+C), and paste it to Claude with this prompt:

"Here's my current Claude Desktop config. Please add a filesystem MCP server that gives access to C:\dev, merge it correctly into my existing mcpServers block, and give me back the complete, valid file to paste. Here's the server I want added:

"filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\dev"], "timeout": 60000 }"

Paste Claude's version back into the JSON file, save, then restart Claude (top-left menu → File → Exit, then reopen).
Confirm it worked by asking: "List what's in C:\dev\XMotion\Captures and tell me which image sets look ready to review."

---

## Part 8 — Airbnb Research & Scoring

This is the engine of the whole operation: **find great properties, and prove they're walkthrough-grade.** Two loops run every day — you source the candidates, Claude sharpens your judgment and scores the results. Get good at this and you're the reason listings sell.

### Reference the skill files first
Two skill files hold our standards. Pull them into any chat so Claude grades by *our* rules, not generic ones:
- Type **`/XM`** — select **/XMotion-Shot-Quality-Equation**
- New line (Shift + Enter), type **`/XM`** again — select **/XMotion-Higgsfield-Walkthrough**
- Continue your prompt on the next line

(You can also point Claude at `C:\dev\XMotion\AI Skills`, but those files may lag — `/XM` is cleaner and always current.)

### Loop 1 — Source 9 candidates (your eyes, Claude's judgment)
Discovery is **your** job — you can browse and filter Airbnb in ways Claude can't. Put in real effort: open listings, study the photos, and find **9 strong candidates.** What you're hunting for:
- Open-plan or clearly connected rooms — a readable path through the space
- Bright, natural light
- 15+ listing photos
- A clear room-to-room flow that could animate into a smooth walkthrough

Then bring your 3 to Claude with a quick one-line read on each, and let it pressure-test your picks:

> *"Below are 3 Airbnb listings I found as walkthrough candidates, each with my quick note. Check my read against our standard — open-plan or clearly connected, bright natural light, 15+ photos, clear room-to-room flow. Rank all 9 best to worst (1-99), tell me why for each, and tell me which to capture first. Don't score the equation yet — that comes after I capture."*
>
> *1. [link] — my note: …*
> *2. [link] — my note: …*
> *3. [link] — my note: …*
> 

Claude ranks them; you capture the top picks with XCopy (Part 6).

### Loop 2 — Score a captured set
Once you've captured a listing, Claude automatically grades the real photos against our **Shot Quality Equation**. Here's the system in brief, so the numbers Claude gives you mean something:

**How the scoring works (Image Scorer v2 — the current standard):**

```
Score = √( Flow × Quality × Location × MoneyShot ) / √( Ambiguity × Noise )
```

Every factor is a **1–99 integer** — one scale family everywhere. The four on top are what the shot *offers* (how well rooms connect, how good the photo is, how strong the market, whether there's a hero frame). The two on the bottom are what works *against* it: **Ambiguity** (can the space be reconstructed, or will the AI hallucinate the layout?) and **Noise** (compression, blur, watermarks, low resolution). Averaged across a block, the full ratio gives the catalog's **Shot Potential (ⲱ)**.

The bottom of the fraction alone is the **pre-shot gate**, called Set Degradation:

```
⊜ = √( Ambiguity × Noise )     →   ⊜ ≤ 20 PASS  ·  20–30 MAYBE  ·  > 30 FAIL
```

The gate exists to protect credits: a FAIL block gets logged as abandoned and never generated, no matter how pretty individual photos are. Ambiguity is deliberately the dominant failure mode — a clean photo of a confusing space is more dangerous than a soft photo of a clear one, because the AI will confidently invent rooms that don't exist.

> *(If you see old notes with scores like "SD = 2.83" — that's the retired 1–9 scale. Multiply by ~10 to translate: old 2.0 PASS ≈ new 20 PASS. Same verdicts, new numbers.)*

Reference the skill files, then:

> *"Hi, this is [your name]. Batch-grade the thumbnails at `C:\dev\XMotion\Captures\[date]\[block]\TN_[block]` for walkthrough potential — read them efficiently as a batch, not one by one. Be honest: does it pass our standard? Give me the ⊜ gate verdict, the Shot Potential (ⲱ), the keeper frames in walkthrough order, and what to drop."*

**Practice on the sample first.** Your repo ships with a real block at `Captures\2026-06-27\PM_3-59_4-04`. Run the scoring prompt on it — you should get close to this:

> **PM_3-59_4-04** — Noise ~20 (clean gallery exports). Ambiguity 40 as-is → 20 once cut to unit-flow. **⊜ = √(40×20) ≈ 28 → MAYBE as-is → √(20×20) = 20 → PASS after light prep.** A well-styled open studio, prime walkthrough material — one FPV sweep traverses the whole space. Keepers in order: 003 → 001 → 010 → 005 → 008 → 009 → 011. Drop the redundant wides (002, 006); hold the vignettes (004, 007) as B-roll; amenities as an optional coda.

If your result looks like that, your setup works and you've seen the bar. That's the standard.

### The order that matters
**Source → Capture → Score.** You can't score a property you haven't captured — the equation needs the real photos not just links. Find them, capture the best, grade them, produce them in week 2.

---

##### **The Goal**

Find Airbnb listings where you can confidently predict a property’s walkthrough potential by evaluating three key variables:

1. **Room‑to‑room flow** — how well the photos connect the space visually
    
2. **Image and property quality** — brightness, staging, and overall listing presentation
    
3. **Market location** — using the pre‑built location charts in `\XMotion\Analysis\Locations
    

Mastering these three variables turns sourcing from guesswork into a repeatable skill.

---

## Part 9 — Power-Ups: the extended toolkit *(optional, once Parts 1–8 are solid)*

Everything up to here gets you producing. This part makes Claude *smarter over time*. Five power-ups, and here's the key thing to understand before installing any of them:

> **Only one of these is an "MCP server" that goes in your config file.** The other four are **skills and plugins** — they install differently and live in different places. Knowing which is which saves you an hour of confusion.

**The three layers, in plain English:**
- **MCP servers** = Claude's *hands*. They live in `claude_desktop_config.json` and let Claude touch things (your files, your windows, its memory). You already have these from Parts 3 and 7.
- **Skills** = Claude's *training*. Markdown instruction files that teach Claude a specific craft. They auto-trigger when relevant. Our `/XM` files are skills.
- **Plugins** = Claude's *reflexes*. They hook into Claude Code (the coding version of Claude) and fire automatically at certain moments — session start, after a tool runs, etc.

### 9.0 — The canonical config (reference)

This is what a fully-loaded `claude_desktop_config.json` looks like on a team machine. Replace `YOUR-USERNAME` with your Windows username. **Only touch the `mcpServers` block** — if your file has other keys (like `preferences`), leave them exactly as they are; they're machine-specific.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "C:\\Users\\YOUR-USERNAME\\AppData\\Roaming\\npm\\mcp-server-filesystem.cmd",
      "args": ["C:\\dev"],
      "timeout": 60000
    },
    "windows-mcp": {
      "command": "C:\\Users\\YOUR-USERNAME\\.local\\bin\\windows-mcp.exe",
      "args": [],
      "timeout": 120000
    },
    "memory": {
      "command": "C:\\Users\\YOUR-USERNAME\\AppData\\Roaming\\npm\\mcp-server-memory.cmd",
      "args": [],
      "timeout": 60000
    },
    "sequential-thinking": {
      "command": "C:\\Users\\YOUR-USERNAME\\AppData\\Roaming\\npm\\mcp-server-sequential-thinking.cmd",
      "args": [],
      "timeout": 60000
    },
    "claude-mem-search": {
      "command": "node",
      "args": ["C:\\Users\\YOUR-USERNAME\\.claude\\plugins\\marketplaces\\thedotmack\\plugin\\mcp-server.cjs"],
      "timeout": 60000
    }
  }
}
```

Notes on this block:
- If your servers were installed with `npx` (the Part 3 style), that works too — the `.cmd` paths above are just the direct-install form and start faster.
- The `claude-mem-search` entry **only works after you install claude-mem in 9.3** — add it last, and ask Claude to verify the exact path to `mcp-server.cjs` on your machine first, since the plugin folder location can vary by version.
- After any config change: save, fully exit Claude (top-left menu → File → Exit), reopen.

### 9.1 — Find Skills *(skill — the app store browser)*

**What it is:** A meta-skill that turns Claude into its own package manager. When you ask "is there a skill for X?" or "how do I do X?", it searches the open skills registry (skills.sh), checks quality signals like install counts and source reputation, and offers to install what it finds.

**Install** (paste into a terminal):
```
npx skills add vercel-labs/skills --skill find-skills -g -y
```
The `-g` installs it globally so it's available in every project.

**How to use it strategically:** This is the *first* power-up to install because it's the gateway to all the others — once it's in, you discover tools by asking instead of Googling. The workflow discipline: when you hit a task that feels like "someone must have solved this before" (PDF wrangling, changelog writing, accessibility checks), ask Claude *"is there a skill for this?"* before building a manual workflow. One caution: not everything in the registry is good. Prefer skills with 1K+ installs from known sources (vercel-labs, anthropics), and ask Claude to summarize what a skill does before installing it. Treat it like the app store — browse with judgment.

**Where it works:** Skills install into agent skill folders (`.claude/skills/`, `.agents/skills/`), which coding agents like Claude Code read natively. Regular Desktop *chat* doesn't auto-load these folders — for chat, the `/XM` pattern (account-level skills) remains our delivery method. Practical rule: **Find Skills lives in your coding sessions; `/XM` lives in your chat sessions.**

### 9.2 — Superpowers *(Claude Code plugin — the senior-engineer discipline)*

**What it is:** A full software development methodology installed as a plugin. Instead of Claude jumping straight into writing code, it brainstorms a spec with you first, writes an implementation plan, then executes with test-driven development and self-review. It's the difference between "intelligent autocomplete" and a disciplined engineer.

**Install** (inside an active Claude Code session — *not* a terminal, not the config file):
```
/plugin install superpowers@claude-plugins-official
```
Then restart the session. Verify with `/plugin` — you should see superpowers listed and active.

**How to use it strategically:** This is for **build days, not production days**. When we're extending XCopy, adding scoring automation, or building a new tool in `_Tools`, Superpowers forces the two habits that prevent expensive rework: (1) the brainstorm phase surfaces the real requirement before any code exists — *read the plan it shows you, don't just approve it*, because a plan you actually read prevents more bugs than any review catches later; and (2) red/green TDD means every change ships with proof it works. For quick throwaway scripts, tell Claude "skip planning, just write it" and the skills stay dormant — it adapts to the stakes. VAs won't need this in Week 1; it becomes relevant the day you graduate from *using* the tools to *improving* them.

**Where it works:** Claude Code only (terminal or the Code tab in the desktop app). It does nothing in regular chat.

### 9.3 — claude-mem *(plugin + MCP server — the long-term memory)*

**What it is:** Persistent memory across sessions. A background observer captures what happens while Claude works — decisions, bug fixes, discoveries — compresses it with AI into a local SQLite database, and injects the relevant history into your next session. The "re-explain everything every morning" tax disappears.

**Install** (terminal):
```
npx claude-mem install
```
> ⚠️ **Do not use `npm install -g claude-mem`** — that installs only the library without registering the hooks or starting the worker. The `npx claude-mem install` command is the whole ceremony.

Then optionally add the `claude-mem-search` MCP entry from 9.0 to your Desktop config, which lets Desktop chat *search* those memories too.

**How does this get along with our existing `memory` server?** They coexist cleanly because they do opposite jobs. The `memory` MCP is a **deliberate** knowledge graph — Claude writes to it when you say "remember that this client prefers X." claude-mem is **automatic** — it captures everything as you work without being asked. Think of `memory` as your labeled filing cabinet and claude-mem as security-camera footage with a search bar. Keep both: use `memory` for facts that must never be lost (client preferences, standing decisions, scoring conventions), and let claude-mem handle ambient session history.

**How to use it strategically:** The payoff compounds. Week one it's learning your project and injecting a lot; after it has mapped your workflow, sessions start faster than before because Claude opens already knowing yesterday's capture blocks, which listings scored PASS, and what you were in the middle of. Two habits maximize it: start sessions by asking *"what were we working on?"* to pull relevant context, and wrap anything sensitive (passwords, client financials) in `<private>` tags in your prompts so it's excluded from storage. Check the web viewer at `localhost:37777` occasionally to see what it's remembering.

**Where it works:** Fully in Claude Code; searchable from Desktop chat once the MCP entry is added.

### 9.4 — Impeccable *(skill — the design taste layer)*

**What it is:** A design-language skill that strips the "obviously AI-generated" tells out of anything visual Claude builds — the default fonts, the purple gradients, the cards-nested-in-cards look. One skill, 23 commands (`/impeccable audit`, `/impeccable polish`, `/impeccable critique`, and more), plus dozens of deterministic detector rules that catch design mistakes automatically.

**Install** (terminal, from the root of the project you're working in):
```
npx impeccable install
```
Then, inside your coding tool: `/impeccable init` — it interviews you once about audience, brand, and voice, and writes that context to `PRODUCT.md`/`DESIGN.md` so every later command designs *for XMotion* instead of generically.

**How to use it strategically:** Our product *is* visual — a listing video with amateur-looking overlays undercuts the entire premium positioning. Use it in a simple cadence: `/impeccable audit` before touching anything (find the issues), make your changes, `/impeccable polish` before anything ships (final cleanup). The `init` step is the strategic part — the ten minutes you spend defining XMotion's brand lane there pays out on every asset afterward, because the skill stops suggesting generic-SaaS aesthetics and starts enforcing *our* look. If you use one command constantly, pin it: `/impeccable pin audit` gives you `/audit` as a shortcut.

**Where it works:** Coding harnesses (Claude Code, Cursor, etc.) working on real UI files. For pure chat-based design discussion, our existing brand skills carry the load.

### 9.5 — Task Observer *(skill — the noticing layer)*

**What it is:** A meta-skill that watches your work sessions and logs opportunities for creating or improving other skills. It captures patterns — moments where you corrected Claude, workflows you repeated three times, techniques that worked unusually well — and saves them as observations for review.

**Install** (terminal):
```
npx skills add rebelytics/one-skill-to-rule-them-all --skill task-observer -g -y
```

**How to use it strategically:** This is how the playbook writes itself. Right now, when a VA discovers a better way to source listings or a scoring shortcut, that insight lives in one person's head and evaporates. With Task Observer running, those moments get logged automatically, and a weekly review ("Claude, show me this week's observations — what should become a skill?") turns them into permanent team capability. One known quirk: it can forget to activate when you're deep in a task, so the reliable setup is adding one line to your project's `CLAUDE.md` telling Claude to invoke it at session start. Pair it with claude-mem and you have a complete learning loop — claude-mem remembers *what happened*, Task Observer notices *what it means*.

**Where it works:** Claude Code sessions, same as other skills.

### 9.6 — The install order that makes sense

1. **Find Skills** first — it's the gateway and takes thirty seconds.
2. **claude-mem** second — the earlier it starts, the more history it has. Add the MCP config entry after confirming the plugin works.
3. **Task Observer** third — it feeds off active work, so install before a real work week.
4. **Superpowers** when you start *building* tools rather than using them.
5. **Impeccable** when you touch anything visual — run `/impeccable init` the same day.

After each install, the check is always the same: restart, ask Claude *"do you have access to [tool]?"*, and have it demonstrate once before relying on it.

---
## You're set

That's the workstation. To recap what you now have: Claude that can control your PC and read your project files, the capture tool ready to shoot listings, Obsidian to learn from, and your email for customers. And when you're ready to level up, Part 9 turns that workstation into a system that remembers, notices, and improves itself.

Welcome aboard. Let's build something nobody's done yet.

— Collin
