"""Cross-platform clipboard integration with native OS fallbacks."""

from __future__ import annotations

import platform
import shutil
import subprocess
import pyperclip


def copy_to_clipboard(text: str) -> tuple[bool, str]:
    """Copy text to system clipboard using pyperclip with native OS fallbacks.

    Returns:
        (success: bool, detail: str)
    """
    # 1. Primary attempt using pyperclip
    try:
        pyperclip.copy(text)
        return True, "Copied via pyperclip"
    except Exception as exc:
        pyperclip_err = str(exc)

    # 2. Native OS fallbacks
    system = platform.system().lower()

    if system == "windows":
        try:
            # Windows 'clip.exe' takes piped input (encode to utf-16le or utf-8)
            subprocess.run(
                ["clip"],
                input=text.encode("utf-16le"),
                check=True,
                shell=False,
            )
            return True, "Copied via Windows clip"
        except Exception as win_exc:
            return False, f"Failed copying to clipboard: {win_exc} (pyperclip: {pyperclip_err})"

    elif system == "darwin":  # macOS
        if shutil.which("pbcopy"):
            try:
                subprocess.run(
                    ["pbcopy"],
                    input=text.encode("utf-8"),
                    check=True,
                )
                return True, "Copied via macOS pbcopy"
            except Exception as mac_exc:
                return False, f"Failed copying via pbcopy: {mac_exc}"

    elif system == "linux":
        # Check for Wayland (wl-copy)
        if shutil.which("wl-copy"):
            try:
                subprocess.run(
                    ["wl-copy"],
                    input=text.encode("utf-8"),
                    check=True,
                )
                return True, "Copied via Wayland wl-copy"
            except Exception:
                pass

        # Check for xclip
        if shutil.which("xclip"):
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode("utf-8"),
                    check=True,
                )
                return True, "Copied via xclip"
            except Exception:
                pass

        # Check for xsel
        if shutil.which("xsel"):
            try:
                subprocess.run(
                    ["xsel", "--clipboard", "--input"],
                    input=text.encode("utf-8"),
                    check=True,
                )
                return True, "Copied via xsel"
            except Exception:
                pass

    return False, f"Clipboard unavailable (pyperclip failed: {pyperclip_err})"
