---
title: XMotion — Week 1 Quick Start Guide
type: onboarding
audience: new-va
status: active
version: 1.0
updated: 2026-06-27
tags: [xmotion, onboarding, setup, week-1, workstation]
author: Collin
name: XMotion Week 1 Onboarding
description: Week-1 workstation setup track for new VAs. Use when onboarding a new team member, walking through app or MCP installation, fixing a config issue, or re-verifying a VA workstation. Trigger on setup, onboarding, week 1, install, config, MCP, or a VA first session. Covers core app installs, team accounts, windows-mcp keystone setup, the C:/dev/XMotion workspace, Obsidian vault, the XCopy capture tool, filesystem access, and the sourcing and scoring loops.
growth:
  - Week 2 production guide: first generation session with Higgsfield
  - Fold in the VA capture-location decision once resolved (VPS vs local, D-2)
  - Move shared credentials out of this doc to a secure channel before any repo sync
---

# XMotion — Week 1 Quick Start Guide

Welcome to the team,
XMotion turns ordinary property photos into cinematic walkthrough videos that help listings sell — and you're getting in early, while we're still writing the playbook together. That's the best time to join anything.

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
winget install -i -e --id 9NRX63209R7B --source msstore --accept-package-agreements
```

What each one is:
- **Claude** — your AI assistant and main tool. [claude.ai/download](https://claude.ai/download)
- **Obsidian** — where you'll read guides like this one and log your work. [obsidian.md/download](https://obsidian.md/download)
- **Alacritty** — a terminal window (we'll customize it in a fun way in Part 5). [alacritty.org](https://alacritty.org)
- **Node.js** — runs behind the scenes so Claude's tools work. (No window opens — that's normal.)
- **Python** — runs the photo capture tool. (Also no window — normal.)
- **Git** — will use later for refreshing the obsidian vault or an automatic sync
- **Power Toys** — set Fancy Zones to priority for efficiency (hold shift while moving a window to lock it to a zone)
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

This is the fun part. You're going to have Claude set itself up to control your Windows PC. This is called **Windows MCP**, and once it's on, Claude can create folders, edit files, and run programs *for* you.

**Step 3.1 — Introduce yourself.** Open a **new chat** in Claude, make sure the model is set to **Opus** (top of the chat), and paste this:

> *Hi Claude, My name is Richlan/Jaisa, I'm a new XMotion team member setting up my workstation. I'm not very technical, so please keep instructions simple and step-by-step. I want to set up three MCP servers in my Claude Desktop config: **windows-mcp** (so you can control my Windows PC), **memory**, and **sequential-thinking**. Can you walk me through installing windows-mcp and give me the exact JSON to paste? My computer is Windows.*

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
Prompt 1: *I'm trying to find the right hex codes that would look good on on a transparent background. These are the colors i'm currently considering 
 (#99FF99) as the primary and (#5f9EA0) as the secondary text color can you create a simple but abstract react artifact using these two colors on a glasmophic background."

 **Verify what colors you want your panel text to be or search for hex codes based on your color preferences**

### Windows MCP 
Prompt 2: *Using windows-mcp, please edit my Alacritty config file (`alacritty.toml`, usually in `%APPDATA%\alacritty\`). Set the window opacity to `0.33` and the text primary color to (#99FF99) and secondary text color to (#5f9EA0), "secondary" is dim_foreground (dimmed text). Create the file if it doesn't exist.*

Open Alacritty afterward — it should be see-through with a soft green tint. You just edited a system config file without touching a line of code yourself. That's the workflow for everything from here.

### XCopy (Automation Tool)

The capture tool (**XCopy**) grabs listing photos into organized folders. Open alacrity, paste this command line in with ctrl + shift + v

cd C:\dev\XMotion\_Tools
py -m pip install pillow
py XCopy.py -5


- Line 1 moves into the tools folder.
- Line 2 installs `pillow` (an image library the tool needs).
- Line 3 launches XCopy.

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

Then bring your 9 to Claude with a quick one-line read on each, and let it pressure-test your picks:

> *"Below are 9 Airbnb listings I found as walkthrough candidates, each with my quick note. Check my read against our standard — open-plan or clearly connected, bright natural light, 15+ photos, clear room-to-room flow. Rank all 9 best to worst (1-99), tell me why for each, and tell me which to capture first. Don't score the equation yet — that comes after I capture."*
>
> *1. [link] — my note: …*
> *2. [link] — my note: …*
> *(…through 9)*

Claude ranks them; you capture the top picks with XCopy (Part 6).

### Loop 2 — Score a captured set
Once you've captured a listing, Claude grades the real photos against our Shot Quality Equation. Reference the skill files, then:

> *"Hi, this is [your name]. Batch-grade the thumbnails at `C:\dev\XMotion\Captures\[date]\[block]\TN_[block]` for walkthrough potential — read them efficiently as a batch, not one by one. Be honest: does it pass our standard? Give me the score, the keeper frames in walkthrough order, and what to drop."*

**Practice on the sample first.** Your repo ships with a real block at `Captures\2026-06-27\PM_3-59_4-04`. Run the scoring prompt on it — you should get close to this:

> **PM_3-59_4-04** — Noise ~2 (clean gallery exports). Ambiguity 4 as-is → 2 once cut to unit-flow. **SD = √(4×2) ≈ 2.83 → MAYBE as-is → √(2×2) = 2.0 → PASS after light prep.** A well-styled open studio, prime walkthrough material — one FPV sweep traverses the whole space. Keepers in order: 003 → 001 → 010 → 005 → 008 → 009 → 011. Drop the redundant wides (002, 006); hold the vignettes (004, 007) as B-roll; amenities as an optional coda.

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
## You're set

That's the workstation. To recap what you now have: Claude that can control your PC and read your project files, the capture tool ready to shoot listings, Obsidian to learn from, and your email for customers.

Welcome aboard. Let's build something nobody's done yet.

— Collin
