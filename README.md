# promptcat

**Offline, deterministic prompt compiler and text improver for command-line power users.**

`promptcat` transforms messy user ideas, raw pasted specifications, and unformatted notes into clean, structured, high-context prompts ready for AI coding assistants.

> **Zero AI. Zero LLMs. Zero external APIs. Zero network calls.**  
> `promptcat` is a local, deterministic text compiler. For identical input and settings, the generated output is always 100% identical.

---

## What's New in this Version

* **Easy Interactive Checkbox Stack Selection**: No more guessing what to type! Select popular technologies (React, Next.js, FastAPI, PostgreSQL, etc.) using simple checkboxes, let promptcat auto-detect from your idea, or type a custom stack.
* **Template Format Choice (`XML` vs `Markdown`)**: Choose `--format xml` (default, tailored for Claude / Anthropic) or `--format markdown` (tailored for ChatGPT, Cursor, and Markdown files).
* **Offline Token Estimator**: Instantly see estimated token and character counts (`~420 tokens | 1,290 chars`) computed locally via deterministic subword estimation.
* **Local Prompt History**: Automatically saves your compiled prompts in an offline, private SQLite database. View recent prompts with `promptcat history`, inspect past prompts with `promptcat --history-show <ID>`, or re-copy your last prompt with `promptcat --last`!
* **1-Click Beginner Installation**: Friends can simply clone the repo and double-click `install.bat` (or run `pip install .`) to install promptcat globally—no virtual environment setup required!

---

## The Core Pipeline

```text
RAW USER INPUT
      ↓
TEXT CLEANER (Whitespace, Contractions, Typos, Casing, Punctuation)
      ↓
RULE ANALYZER (Domain Detection: Auth, DB, API, UI, Testing, Performance)
      ↓
PROMPT ENHANCER (Role, Task, Context, Tech Stack, Constraints, Requirements)
      ↓
TEMPLATE COMPILER (XML or Markdown Structured Format)
      ↓
TOKEN ESTIMATOR (Offline BPE Subword Estimation)
      ↓
LOCAL SQLITE HISTORY (Saved locally in ~/.promptcat/history.db)
      ↓
CLIPBOARD / TERMINAL / FILE
```

---

## 1-Minute Quickstart

### Method A: One-Click (Windows)
Double-click `install.bat`. It installs `promptcat` globally on your machine.

### Method B: Via Terminal (Any OS)
Requires Python 3.11+:
```bash
pip install .
```
Or directly from GitHub:
```bash
pip install git+https://github.com/ziankyle-mi/prompt.cat.git
```

Now you can open **any terminal anywhere** and just type:
```bash
promptcat "your idea here"
```

---

## Usage

### 1. Interactive Wizard Mode (Beginner-Friendly)

Simply run:
```bash
promptcat -i
```
Or double-click `promptcat.bat` on Windows!

The wizard guides you with clear menus:
1. **What do you want to build or improve?** (Type your idea)
2. **Select mode:**
   - `Improve` (Senior architecture & plan — Recommended)
   - `Feature` (Complete implementation, edge cases & tests)
   - `Debug` (Root-cause diagnosis & surgical fix)
   - `Refactor` (Code cleanup & zero regressions)
   - `Grammar` (Fix typos, punctuation & formatting only)
3. **Select format:**
   - `XML` (Best for Claude / Anthropic)
   - `Markdown` (Best for ChatGPT / Cursor)
4. **Choose tech stack with checkboxes:** (Spacebar to toggle choices like `React`, `Next.js`, `FastAPI`, `PostgreSQL`, or press Enter to let promptcat auto-detect from your idea)

---

### 2. Fast Command-Line Usage

```bash
# Basic prompt compilation
promptcat "make a login page using react but idk how to make the backend and make it secure"

# Markdown format (ideal for ChatGPT & Cursor)
promptcat "Build a REST API with FastAPI" --format markdown

# Feature mode with explicit stack
promptcat "Add Stripe checkout" --mode feature --stack "Next.js,Stripe,PostgreSQL"

# Debug mode
promptcat "JWT tokens expire immediately on Safari" --mode debug

# Text cleaner only
promptcat "dont use mongo use postgres and make teh ui responsive" --clean-only
```

---

### 3. Local Prompt History

Never lose a generated prompt:

```bash
# View recent prompt history table
promptcat history

# Re-copy your last compiled prompt straight to clipboard
promptcat --last

# View and copy a specific prompt by its ID
promptcat --history-show 12

# Clear your history
promptcat --clear-history
```

---

## CLI Options

```text
Usage: promptcat [OPTIONS] [TEXT]

Arguments:
  [TEXT]  Raw text or idea to compile. Can also be piped via stdin.

Options:
  -m, --mode TEXT              improve, feature, debug, refactor, grammar. [default: improve]
  -F, --format TEXT            xml or markdown. [default: xml]
  -s, --stack TEXT             Comma-separated tech stack (e.g. 'react,postgresql').
  -c, --copy / --no-copy       Copy compiled prompt to clipboard. [default: copy]
  -f, --file PATH              Read input text from a file.
  -o, --output PATH            Save compiled prompt to a file.
  -H, --history                View recent prompt history table.
  -l, --last                   View and re-copy most recent prompt from history.
  --history-show INTEGER       View and copy prompt by history ID.
  --clear-history              Clear stored prompt history.
  --clean-only                 Run text cleaner only and print result.
  --detect-only                Run domain detection only and print findings.
  --raw                        Print only compiled prompt text.
  -i, --interactive            Launch interactive questionnaire.
  -v, --version                Show promptcat version.
  --help                       Show this message and exit.
```

---

## Testing

Run the full deterministic test suite (45 tests):

```bash
pytest -v
```

---

## License

MIT License.
