# promptcat

**Offline, deterministic prompt compiler and text improver for command-line power users.**

`promptcat` transforms messy user ideas, raw pasted specifications, and unformatted notes into clean, structured, high-context prompts ready for AI coding assistants.

> **Zero AI. Zero LLMs. Zero external APIs. Zero network calls.**  
> `promptcat` is a local, deterministic text compiler. For identical input and settings, the generated output is always 100% identical.

---

## The Core Pipeline

```text
RAW USER INPUT
      ↓
TEXT CLEANER (Whitespace, Contractions, Typos, Casing, Punctuation)
      ↓
RULE ANALYZER (Domain Detection: Auth, DB, API, UI, Testing, etc.)
      ↓
PROMPT ENHANCER (Role, Task, Context, Tech Stack, Constraints, Requirements)
      ↓
TEMPLATE COMPILER (XML-Structured LLM Prompt)
      ↓
FINAL PROMPT
      ↓
CLIPBOARD / TERMINAL / FILE
```

---

## Features

* **Deterministic Text Hygiene**: Normalizes whitespace, fixes unambiguous contractions (`dont` &rarr; `don't`), corrects common typos (`teh` &rarr; `the`), preserves code blocks, fixes misplaced punctuation, and standardizes acronyms (`ui` &rarr; `UI`, `api` &rarr; `API`, `jwt` &rarr; `JWT`).
* **Domain Detection & Constraint Injection**: Analyzes input with keyword and regex rules to detect domains (Authentication, Database, API, Frontend, Testing, Performance) and injects engineering constraints.
* **Modes for Different Workflows**:
  * `improve`: Turns rough ideas into structured engineering tasks.
  * `feature`: Outlines architecture, edge cases, implementation, tests, and verification.
  * `debug`: Isolates symptoms, enforces root-cause diagnosis, minimal fixes, and regression prevention.
  * `refactor`: Structural cleanup, behavior preservation, modularity, and zero regressions.
  * `grammar`: Returns cleaned, formatted text directly without prompt scaffolding.
* **Cross-Platform Clipboard**: Copies directly to the clipboard via `pyperclip`, with native OS fallbacks (`clip` on Windows, `pbcopy` on macOS, `wl-copy`/`xclip` on Linux).
* **Minimal, Semantic Terminal UI**: Clean status tags (`[OK]`, `[INFO]`, `[WARN]`, `[ERROR]`) rendered via `rich`. Strictly no emojis.

---

## Installation

### From Source

Requires Python 3.11+:

```bash
# Clone or navigate to the repository
cd prompt.cat

# (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install promptcat
pip install -e .
```

---

## Usage

### 1. Basic Prompt Improvement

```bash
promptcat "i want to make a login page using react but idk how to make the backend and make it secure"
```

Output:
```text
[OK] Text cleaned
[OK] Authentication detected
[OK] API detected
[OK] Frontend detected
[OK] Technologies: React
[OK] Prompt compiled (Mode: improve)
[OK] Copied to clipboard

<role>
You are a Senior Software Engineer and Systems Architect. Your objective is to design and implement robust, maintainable, and production-ready solutions.
</role>

<task>
Design and implement the following requirement with high code quality and clear architectural separation:
I want to make a login page using React but I don't know how to make the backend and make it secure.
</task>
...
```

### 2. Feature Mode with Explicit Stack

```bash
promptcat "Build user settings with avatar upload" --mode feature --stack "React,FastAPI,PostgreSQL"
```

### 3. Debugging Mode

```bash
promptcat "Tokens expire immediately after login on Safari" --mode debug
```

### 4. Text Cleaner Only (`--clean-only`)

```bash
promptcat "dont use a database and make teh ui nice   and responsive" --clean-only
```

Output:
```text
[OK] Text cleaned
[INFO] Correction: Normalized whitespace and line breaks
[INFO] Correction: Corrected contraction: 'dont' -> 'don't' (1x)
[INFO] Correction: Corrected typo: 'teh' -> 'the' (1x)
[INFO] Correction: Standardized casing: 'ui' -> 'UI'
[INFO] Correction: Capitalized start of lines
[INFO] Correction: Added terminal punctuation

Don't use a database and make the UI nice and responsive.
```

### 5. Domain Detection Only (`--detect-only`)

```bash
promptcat "Build a JWT login API using PostgreSQL and React" --detect-only
```

Output:
```text
[OK] Authentication detected (login, jwt)
[OK] Database detected (postgresql)
[OK] API detected (api)
[OK] Frontend detected (react)
[INFO] Detected technologies: React, PostgreSQL, JWT
```

### 6. Piped Input & Raw Output for Automation

```bash
cat feature_idea.txt | promptcat --mode feature --raw
```

Or write output directly to a file:

```bash
promptcat "Refactor payment processor" --mode refactor -o prompt.xml
```

### 7. Interactive Mode

Run `promptcat` without arguments (in an interactive terminal) or pass `--interactive` / `-i`:

```bash
promptcat -i
```

Interactive prompts will ask:
- What do you want to build or improve?
- Select mode (`Improve`, `Grammar`, `Feature`, `Debug`, `Refactor`)
- Optional tech stack

---

## CLI Reference

```text
Usage: promptcat [OPTIONS] [TEXT]

Arguments:
  [TEXT]  Raw text or idea to compile. Can also be piped via stdin.

Options:
  -m, --mode TEXT        Compilation mode: improve, grammar, feature, debug, refactor. [default: improve]
  -s, --stack TEXT       Comma-separated tech stack (e.g. 'react,postgresql').
  -c, --copy / --no-copy Copy compiled prompt to clipboard. [default: copy]
  -f, --file PATH        Read input text from a file.
  -o, --output PATH      Save compiled prompt to a file.
  --raw                  Print only the compiled prompt text.
  --clean-only           Run text cleaner only and print result.
  --detect-only          Run domain detection only and print findings.
  -i, --interactive      Launch interactive questionnaire.
  -v, --version          Show promptcat version.
  --help                 Show this message and exit.
```

---

## Architecture & Project Structure

```text
promptcat/
│
├── promptcat/
│   ├── __init__.py      # Package metadata & public exports
│   ├── models.py        # Core dataclasses (PromptRequest, CompiledPrompt, etc.)
│   ├── cleaner.py       # Deterministic text cleanup engine
│   ├── rules.py         # Domain detection and constraint registry
│   ├── templates.py     # XML-style prompt templates for each mode
│   ├── compiler.py      # Pipeline orchestrator
│   ├── clipboard.py     # Clipboard handler with OS fallbacks
│   ├── output.py        # Semantic Rich terminal output (no emojis)
│   └── cli.py           # Typer CLI application
│
├── tests/
│   ├── test_cleaner.py   # Cleaner unit tests
│   ├── test_rules.py     # Rules & domain detection tests
│   ├── test_compiler.py  # Compiler tests & determinism checks
│   ├── test_clipboard.py # Clipboard fallback tests
│   └── test_cli.py       # Typer CLI integration tests
│
├── requirements.txt
├── pyproject.toml
├── SPECIFICATION.md     # Full design specification
└── README.md
```

---

## Extending promptcat

### Adding a Custom Domain Rule

Domains are extensible without modifying the compiler:

```python
from promptcat.rules import DomainRule, RuleRegistry

registry = RuleRegistry()
registry.register(
    DomainRule(
        name="Blockchain",
        keywords=["solidity", "smart contract", "ethereum", "web3"],
        constraints=[
            "Audit contracts for reentrancy and integer overflow vulnerabilities.",
            "Minimize gas consumption in loops and state mutations.",
        ],
    )
)
```

---

## Testing

Run the test suite using `pytest`:

```bash
pytest -v
```

All 38 test cases execute deterministically and offline in under a second.

---

## License

MIT License.
