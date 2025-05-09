# integration/direct_practice_integration.py

import tkinter as tk
from tkinter import ttk, Frame

# Import the direct practice module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from direct_practice_module import DirectPracticeModule


class DirectPracticeIntegration:
    """Integration class for adding direct practice to existing applications"""
    
    def __init__(self, parent_app=None):
        """Initialize the integration
        
        Args:
            parent_app: Reference to the parent application for data sharing
        """
        self.parent_app = parent_app
    
    def create_practice_tab(self, notebook, tab_name="Direct Practice"):
        """Create a direct practice tab in an existing notebook
        
        Args:
            notebook: Tkinter notebook widget to add the tab to
            tab_name: Name for the practice tab
            
        Returns:
            The created tab frame
        """
        # Create a new tab frame
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=tab_name)
        
        # Add the direct practice module to the tab
        direct_practice = DirectPracticeModule(tab_frame, self.parent_app)
        
        return tab_frame
    
    def create_standalone_window(self, parent_window=None, title="Direct Practice"):
        """Create a standalone window for direct practice
        
        Args:
            parent_window: Parent Tkinter window (for modal behavior)
            title: Window title
            
        Returns:
            The created Toplevel window
        """
        # Create a new top-level window
        if parent_window:
            window = tk.Toplevel(parent_window)
        else:
            window = tk.Toplevel()
        
        window.title(title)
        window.geometry("900x700")
        
        # Add the direct practice module to the window
        direct_practice = DirectPracticeModule(window, self.parent_app)
        
        return window
    
    def create_landing_page(self, container_frame):
        """Create a direct practice landing page in an existing frame
        
        Args:
            container_frame: Frame to place the direct practice in
            
        Returns:
            The direct practice module instance
        """
        # Add the direct practice module to the container
        direct_practice = DirectPracticeModule(container_frame, self.parent_app)
        
        return direct_practice


# Example usage
if __name__ == "__main__":
    # Create a simple test window
    root = tk.Tk()
    root.title("Direct Practice Integration Test")
    root.geometry("900x700")
    
    # Create notebook with tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Create a tab for home
    home_tab = ttk.Frame(notebook)
    notebook.add(home_tab, text="Home")
    
    # Add some dummy content to home tab
    ttk.Label(home_tab, text="Welcome to the test application", 
              font=("Arial", 16, "bold")).pack(pady=20)
    ttk.Button(home_tab, text="Open Standalone Practice", 
              command=lambda: DirectPracticeIntegration().create_standalone_window(root)).pack(pady=10)
    
    # Integrate direct practice as a tab
    integration = DirectPracticeIntegration()
    practice_tab = integration.create_practice_tab(notebook, "Practice Tab")
    
    # Run the application
    root.mainloop()