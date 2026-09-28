# promptcat 🐱

Turn messy thoughts into clean, structured prompts for ChatGPT, Claude, and Cursor.

* **100% Offline** — No AI, no API keys, no internet needed.
* **Auto-copies to clipboard** — Run it, switch to your AI, and press `Ctrl + V`.

---

## ⚡ Install (1 Command)

```bash
pip install git+https://github.com/ziankyle-mi/prompt.cat.git
```

*On Windows, you can also clone this repo and double-click `install.bat`.*

---

## 🚀 How to Use

### 1. Quick One-Liner
```bash
promptcat "make a login page using react but idk how to make the backend and make it secure"
```

### 2. Interactive Menu
Don't want to remember commands? Just run:
```bash
promptcat -i
```
Select your mode and pick your tech stack using the spacebar.

### 3. ChatGPT / Cursor Format
```bash
promptcat "build a rest api with fastapi" --format markdown
```

### 4. Re-copy Last Prompt
```bash
promptcat --last
```

---

## 🎯 Modes

| Mode | Use When | Example |
|---|---|---|
| **`improve`** *(default)* | Turning a rough idea into an engineering plan | `promptcat "add dark mode"` |
| **`feature`** | Building complete features with tests & edge cases | `promptcat "stripe checkout" -m feature` |
| **`debug`** | Diagnosing bugs with root-cause fixes | `promptcat "token expires on safari" -m debug` |
| **`refactor`** | Cleaning up code without breaking anything | `promptcat "refactor auth middleware" -m refactor` |
| **`clean-only`** | Fixing typos, grammar & punctuation only | `promptcat "dont use mongo" --clean-only` |

---

## 📜 History

```bash
promptcat history          # List recent prompts
promptcat --last           # Copy last prompt back to clipboard
promptcat --clear-history  # Clear saved history
```

---

## License
MIT
