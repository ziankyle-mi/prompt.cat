# promptcat

Turn messy thoughts into clean prompts for ChatGPT, Claude, and Cursor. Works offline. Copies the result to your clipboard.

## Install

```bash
pip install git+https://github.com/ziankyle-mi/prompt.cat.git
```

## Use

```bash
promptcat "make a login page using react but idk how to make the backend"
```

Then press `Ctrl + V` in your AI chat.

## Options

- `-i` opens the interactive menu
- `-m feature`, `-m debug`, `-m refactor` change the mode
- `--clean-only` fixes typos and grammar only
- `--format markdown` for ChatGPT and Cursor
- `--last` copies your last prompt again

## License

MIT
