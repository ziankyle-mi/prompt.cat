# promptcat

## 1. Project Overview

Build **promptcat**, an offline, deterministic command-line tool that transforms messy user ideas and large pasted text into cleaner, more structured, higher-context AI prompts.

promptcat does **not** generate answers using AI.

It is a local **prompt compiler and text improver**.

The core pipeline is:

```text
RAW USER INPUT
      ↓
TEXT CLEANER
      ↓
RULE ANALYZER
      ↓
PROMPT ENHANCER
      ↓
TEMPLATE COMPILER
      ↓
FINAL PROMPT
      ↓
CLIPBOARD
```

The tool must work completely offline.

### Core Principles

* **No AI**: Pure deterministic logic.
* **No LLM**: No model inference.
* **No external APIs**: Zero external network dependencies.
* **No network requests**: Fully functional air-gapped.
* **No cloud services**: Local computation only.
* **Deterministic output**: For identical input and settings, output is identical.
* **Large multiline input support**: Handles large pasted blocks and files smoothly.
* **Minimal keyboard-first CLI**: Fast and developer-friendly.
* **Clean terminal UI**: Semantic output with no distracting visual noise.
* **Modular architecture**: Distinct, single-responsibility components.
* **Easy to extend**: Simple plugin-style rule and template addition.

---

## 2. What promptcat Does

promptcat provides four primary capabilities:

### A. Improve
Takes a rough idea and makes it clearer and more structured.

**Example Input:**
```text
i want to make a login page using react but idk how to make
the backend and make it secure
```

**Cleaned Output:**
```text
I want to create a login page using React. I also need a
backend implementation with appropriate security measures.
```

Then enhances it into a structured development prompt.

### B. Grammar Fix
Cleans grammar, spelling, punctuation, capitalization, whitespace, and common typing mistakes.

**Examples:**
```text
i want this to work  →  I want this to work.
dont use a database  →  Don't use a database.
make the ui nice   and responsive  →  Make the UI nice and responsive.
```

This feature is strictly deterministic. It focuses on predictable corrections without rewriting the user's intent.

### C. Prompt Enhancement
Takes the cleaned user idea and adds prompt-engineering structure:
* Role
* Task
* Context
* Technology
* Requirements
* Constraints
* Expected output
* Verification / testing instructions

These are compiled from predefined templates and domain rules.

### D. Domain Detection
Analyzes text using deterministic keyword and regex rules.

**Example:**
```text
Build a JWT login API using PostgreSQL and React.
```

**Detected Domains:**
* Authentication
* API
* Database
* Frontend

Each detected domain injects predefined, domain-specific engineering constraints.

---

## 3. Technology Stack

* **Language**: Python 3.11+
* **CLI Engine**: Typer
* **Interactive UI**: Questionary
* **Terminal Formatting**: Rich (semantic status tags: `[OK]`, `[INFO]`, `[WARN]`, `[ERROR]`, strictly no emojis)
* **Clipboard**: Pyperclip with native platform fallback (`clip` on Windows, `pbcopy` on macOS, `wl-copy`/`xclip` on Linux)
* **Text Processing**: Python standard library (`re`, `unicodedata`, `textwrap`, `dataclasses`, `typing`)
* **Testing**: Pytest
* **Packaging**: `pyproject.toml` exposing entry point `promptcat`

---

## 4. Project Structure

```text
promptcat/
│
├── promptcat/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── cleaner.py
│   ├── rules.py
│   ├── templates.py
│   ├── compiler.py
│   ├── clipboard.py
│   └── output.py
│
├── tests/
│   ├── test_cleaner.py
│   ├── test_rules.py
│   ├── test_compiler.py
│   └── test_clipboard.py
│
├── README.md
├── requirements.txt
├── pyproject.toml
└── SPECIFICATION.md
```

---

## 5. Module Responsibilities

### `models.py`
Data structures powering the pipeline:
* `PromptMode` (Enum: `IMPROVE`, `GRAMMAR`, `FEATURE`, `DEBUG`, `REFACTOR`)
* `PromptRequest` (text, stack, mode, options, role, task, context, constraints)
* `DetectedRule` (domain, matched_keywords, constraints)
* `CleanedText` (original, cleaned, corrections)
* `CompiledPrompt` (raw_input, cleaned_text, mode, detected_domains, stack, prompt_text, metadata)

### `cleaner.py`
Pure deterministic text hygiene:
* Whitespace: Collapse multiple spaces to single, normalize blank lines, strip edges.
* Capitalization: Sentence capitalization, standalone "i" → "I", acronym casing ("ui" → "UI", "api" → "API").
* Contractions: `dont` → `don't`, `cant` → `can't`, `wont` → `won't`, `im` → `I'm`, `ive` → `I've`, `id` → `I'd`.
* Typos: Configurable lookup table (`teh` → `the`, `recieve` → `receive`, `seperate` → `separate`).
* Punctuation: Fix misplaced spaces before punctuation, eliminate duplicate punctuation marks, ensure terminal punctuation.

### `rules.py`
Deterministic domain detection and constraint injection:
* **Authentication**: Detects `auth`, `login`, `jwt`, `session`, `password`, `oauth`, etc.
* **Database**: Detects `database`, `db`, `sql`, `postgres`, `mysql`, `mongodb`, `schema`, `migration`, etc.
* **API**: Detects `api`, `rest`, `endpoint`, `http`, `request`, `response`, `backend`, `server`, etc.
* **Frontend**: Detects `ui`, `frontend`, `component`, `css`, `html`, `react`, `vue`, `interface`, `responsive`, etc.
* **Testing**: Detects `test`, `testing`, `unit test`, `integration`, `pytest`, `jest`, etc.
* Extensible rule registry allowing custom domains without altering the compiler.

### `templates.py`
XML-delimited prompt structures for maximum LLM context adherence:
```xml
<role>
{role}
</role>

<task>
{task}
</task>

<context>
{context}
</context>

<technology>
{technology}
</technology>

<constraints>
{constraints}
</constraints>

<requirements>
{requirements}
</requirements>

<output>
{output}
</output>
```

### `compiler.py`
The orchestrator:
1. Cleans input using `cleaner`.
2. Analyzes domains using `rules`.
3. Merges explicit stack and detected technologies.
4. Generates contextual requirements and constraints based on mode.
5. Injects components into the selected template.
6. Returns a structured `CompiledPrompt`.

### `clipboard.py`
Reliable clipboard interactions:
* Primary attempt via `pyperclip`.
* Graceful fallback to OS binaries (`clip`, `pbcopy`, `wl-copy`/`xclip`).
* Clear success/failure reporting.

### `output.py`
Semantic terminal rendering using Rich:
* Semantic badges: `[OK]`, `[INFO]`, `[WARN]`, `[ERROR]`.
* Clean status logs.
* No emojis or distracting artifacts.

### `cli.py`
Typer command line interface:
* Argument: `promptcat [TEXT]`
* Flags: `--mode`, `--stack`, `--copy / --no-copy`, `--file`, `--output`, `--raw`, `--clean-only`, `--detect-only`, `--interactive`, `--stdin`.
* Interactive questionnaire fallback when no input is supplied.

---

## 6. Prompt Modes

* **Improve Mode**: Converts a rough idea into a structured senior-level development task.
* **Feature Mode**: Outlines architecture, component breakdown, implementation, edge cases, and tests for new capabilities.
* **Debug Mode**: Guides systematic root-cause diagnosis, symptom isolation, minimal atomic fixes, and regression prevention.
* **Refactor Mode**: Focuses on clean code restructuring, modularity, technical debt reduction, and zero functional regressions.
* **Grammar Mode**: Produces deterministic clean text output for instant pasting without prompt framing.
