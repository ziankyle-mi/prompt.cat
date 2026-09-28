"""Tests for promptcat clipboard functionality and fallbacks."""

from unittest.mock import MagicMock, patch
import pytest
from promptcat.clipboard import copy_to_clipboard


class TestClipboard:
    def test_pyperclip_success(self):
        with patch("pyperclip.copy") as mock_copy:
            success, msg = copy_to_clipboard("test text")
            assert success is True
            assert "pyperclip" in msg
            mock_copy.assert_called_once_with("test text")

    def test_windows_clip_fallback(self):
        with patch("pyperclip.copy", side_effect=Exception("Pyperclip failed")):
            with patch("platform.system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    success, msg = copy_to_clipboard("test text")
                    assert success is True
                    assert "clip" in msg
                    mock_run.assert_called_once()
                    args, kwargs = mock_run.call_args
                    assert args[0] == ["clip"]

    def test_macos_pbcopy_fallback(self):
        with patch("pyperclip.copy", side_effect=Exception("Pyperclip failed")):
            with patch("platform.system", return_value="Darwin"):
                with patch("shutil.which", return_value="/usr/bin/pbcopy"):
                    with patch("subprocess.run") as mock_run:
                        success, msg = copy_to_clipboard("test text")
                        assert success is True
                        assert "pbcopy" in msg
                        mock_run.assert_called_once()

    def test_linux_wl_copy_fallback(self):
        with patch("pyperclip.copy", side_effect=Exception("Pyperclip failed")):
            with patch("platform.system", return_value="Linux"):
                with patch("shutil.which", side_effect=lambda cmd: "/usr/bin/wl-copy" if cmd == "wl-copy" else None):
                    with patch("subprocess.run") as mock_run:
                        success, msg = copy_to_clipboard("test text")
                        assert success is True
                        assert "wl-copy" in msg

    def test_total_failure_handled_gracefully(self):
        with patch("pyperclip.copy", side_effect=Exception("Clipboard unavailable")):
            with patch("platform.system", return_value="UnknownOS"):
                success, msg = copy_to_clipboard("test text")
                assert success is False
                assert "Clipboard unavailable" in msg
