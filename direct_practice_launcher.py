#!/usr/bin/env python
# direct_practice_launcher.py

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure the current directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Import the direct practice module
    from direct_practice_module import DirectPracticeModule
    
    # Import base classes for standalone operation
    from parser.study_item import StudyItem, StudyItemCollection, StudyItemType
    from integration.learning_tracker import LearningTracker
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current Python path: {sys.path}")
    print(f"Current directory: {current_dir}")
    sys.exit(1)


class DirectPracticeLauncher:
    """Simple launcher for the direct practice module"""
    
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("PDF/Text Typing Practice")
        self.root.geometry("900x700")
        
        # Initialize minimal required components for standalone operation
        self.study_items = []
        self.study_collection = StudyItemCollection()
        self.learning_tracker = LearningTracker()
        
        # Create the UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the application UI"""
        # Create a simple frame to hold the direct practice module
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the direct practice module
        self.direct_practice = DirectPracticeModule(main_frame, self)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the launcher
    launcher = DirectPracticeLauncher()
    launcher.run()