import os
import sys
import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

# Ensure the app code can be discovered by Python's path loader
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from ui.god_gui import GodStackGUI

class TestGodStackGUI(unittest.TestCase):
    def setUp(self):
        """Initialize Tkinter context before running each test case."""
        self.root = tk.Tk()
        self.app = GodStackGUI(self.root)

    def tearDown(self):
        """Cleanly destroy Tkinter windows to prevent memory leaks across specs."""
        self.app.terminate_engine()
        self.root.destroy()

    def test_url_validation_matrix(self):
        """Verify that the parser accepts well-formed web URLs and catches malformed ones."""
        # Clean URLs
        self.assertTrue(self.app.is_valid_url("https://news.ycombinator.com"))
        self.assertTrue(self.app.is_valid_url("http://localhost:8080"))
        
        # Broken URLs
        self.assertFalse(self.app.is_valid_url("news.ycombinator.com"))
        self.assertFalse(self.app.is_valid_url("ftp://files.server"))
        self.assertFalse(self.app.is_valid_url(""))

    def test_dropdown_and_custom_target_resolution(self):
        """Verify the UI correctly swaps profiles based on selector choices."""
        # Test preset selection rule
        self.app.target_selector.set("https://github.com/trending")
        self.assertEqual(self.app.get_selected_target(), "https://github.com/trending")
        
        # Test custom selection toggle engine rule
        self.app.target_selector.set("CUSTOM")
        self.app.toggle_custom_input(None)
        self.app.custom_url_entry.delete(0, tk.END)
        self.app.custom_url_entry.insert(0, "https://example.com")
        self.assertEqual(self.app.get_selected_target(), "https://example.com")

    @patch("subprocess.Popen")
    def test_subprocess_harness_invocation(self, mock_popen):
        """Verify that the engine spawns Popen with correct environment parameters."""
        # Set up mock subprocess behavior
        mock_proc = MagicMock()
        mock_proc.stdout = []
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc

        # Prime the application inputs
        self.app.target_selector.set("https://news.ycombinator.com")
        self.app.mode_selector.set("--standalone")
        
        # Trigger orchestrator pipeline execution
        self.app.run_orchestrator()

        # Check if subprocess initialization logic captures the correct environment configurations
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        
        self.assertIn("run_stack.sh", args[0][0])
        self.assertEqual(args[0][1], "--standalone")
        self.assertEqual(kwargs["env"]["GOD_TARGET_URL"], "https://news.ycombinator.com")
        self.assertEqual(kwargs["env"]["PYTHONUNBUFFERED"], "1")

    def test_forced_termination_loop(self):
        """Ensure that clicking Stop kills sub-node tracking processes gracefully."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Simulates running process
        self.app.active_process = mock_process
        
        self.app.terminate_engine()
        mock_process.terminate.assert_called_once()

if __name__ == "__main__":
    unittest.main()
