# design_system.py

import tkinter as tk
from tkinter import ttk, font
import os

class TypingStudyDesignSystem:
    """
    Implements the UX/UI design system for the typing study application.
    """
    
    def __init__(self, root, theme="light"):
        self.root = root
        self.theme = theme
        
        # Create design system directories
        self.assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Initialize design tokens
        self._init_tokens()
        
        # Apply base styling
        self._apply_base_styling()
    
    def _init_tokens(self):
        """Initialize design tokens based on design guide"""
        # Typography
        self.fonts = {
            "primary": ("Inter", "sans-serif"),
            "secondary": ("IBM Plex Mono", "monospace"),
            "disfluency": ("JetBrains Mono", "monospace"),
        }
        
        self.weights = {
            "light": font.Font(family=self.fonts["primary"][0], size=10, weight="normal"),
            "regular": font.Font(family=self.fonts["primary"][0], size=12, weight="normal"),
            "semibold": font.Font(family=self.fonts["primary"][0], size=12, weight="bold"),
            "bold": font.Font(family=self.fonts["primary"][0], size=14, weight="bold"),
        }
        
        self.sizes = {
            "body": {"size_px": 16, "line_height": 24, "letter_spacing_px": 0.5},
            "input": {"size_px": 18, "line_height": 28, "letter_spacing_px": 0.75},
            "h1": {"size_px": 32, "line_height": 40},
            "h2": {"size_px": 24, "line_height": 32},
        }
        
        # Color themes
        self.themes = {
            "light": {
                "background": "#FFFFFF", 
                "surface": "#F5F5F5",
                "primary": "#0A84FF", 
                "secondary": "#5E5CE6",
                "text_primary": "#1C1C1E", 
                "text_secondary": "#3A3A3C",
            },
            "dark": {
                "background": "#1C1C1E", 
                "surface": "#2C2C2E",
                "primary": "#0A84FF", 
                "secondary": "#64D2FF",
                "text_primary": "#FFFFFF", 
                "text_secondary": "#EBEBF5",
            },
            "eye_care": {
                "background": "#FFF3E0", 
                "surface": "#FFF8E1",
                "primary": "#FB8C00", 
                "text_primary": "#4E342E",
            }
        }
        
        # Accessibility
        self.accessibility = {
            "focus_outline": "4px auto #0A84FF",
            "aria_live": {
                "input": "polite", 
                "session": "assertive"
            },
            "blue_light_filter": "sepia(0.15) saturate(0.8)",
            "contrast_ratios": {
                "body_text": {"min": 4.5},
                "buttons": {"normal": 3.0, "text": 4.5},
            }
        }
        
        # Get current theme colors
        self.colors = self.themes[self.theme]
    
    def _apply_base_styling(self):
        """Apply base styling to the application"""
        style = ttk.Style()
        
        # Configure base styles
        style.configure(
            "TFrame", 
            background=self.colors["background"]
        )
        
        style.configure(
            "TLabel", 
            background=self.colors["background"],
            foreground=self.colors["text_primary"],
            font=(self.fonts["primary"][0], self.sizes["body"]["size_px"])
        )
        
        style.configure(
            "TButton", 
            background=self.colors["primary"],
            foreground=self.colors["text_primary"],
            font=(self.fonts["primary"][0], self.sizes["body"]["size_px"]),
            padding=8
        )
        
        style.map(
            "TButton",
            background=[("active", self.colors["secondary"])]
        )
        
        style.configure(
            "TEntry",
            fieldbackground=self.colors["surface"],
            foreground=self.colors["text_primary"],
            font=(self.fonts["secondary"][0], self.sizes["input"]["size_px"])
        )
        
        # Configure heading styles
        style.configure(
            "Heading.TLabel",
            font=(self.fonts["primary"][0], self.sizes["h1"]["size_px"], "bold"),
            foreground=self.colors["text_primary"]
        )
        
        style.configure(
            "Subheading.TLabel",
            font=(self.fonts["primary"][0], self.sizes["h2"]["size_px"], "bold"),
            foreground=self.colors["text_primary"]
        )
        
        # Configure special components
        style.configure(
            "StudyInput.TEntry",
            font=(self.fonts["secondary"][0], self.sizes["input"]["size_px"]),
            padding=10
        )
        
        # Configure notebook tabs
        style.configure(
            "TNotebook.Tab",
            background=self.colors["surface"],
            foreground=self.colors["text_primary"],
            padding=[10, 5],
            font=(self.fonts["primary"][0], 12)
        )
        
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["primary"])],
            foreground=[("selected", "#FFFFFF")]
        )
        
        # Configure progress bars
        style.configure(
            "TProgressbar",
            background=self.colors["primary"],
            troughcolor=self.colors["surface"]
        )
    
    def create_theme_toggle(self, parent):
        """Create a theme toggle widget"""
        frame = ttk.Frame(parent)
        
        theme_var = tk.StringVar(value=self.theme)
        
        ttk.Label(frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        
        light_rb = ttk.Radiobutton(
            frame, 
            text="Light", 
            value="light", 
            variable=theme_var,
            command=lambda: self.set_theme("light")
        )
        light_rb.pack(side=tk.LEFT, padx=5)
        
        dark_rb = ttk.Radiobutton(
            frame, 
            text="Dark", 
            value="dark", 
            variable=theme_var,
            command=lambda: self.set_theme("dark")
        )
        dark_rb.pack(side=tk.LEFT, padx=5)
        
        eye_rb = ttk.Radiobutton(
            frame, 
            text="Eye Care", 
            value="eye_care", 
            variable=theme_var,
            command=lambda: self.set_theme("eye_care")
        )
        eye_rb.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def set_theme(self, theme_name):
        """Set the application theme"""
        if theme_name in self.themes:
            self.theme = theme_name
            self.colors = self.themes[theme_name]
            self._apply_base_styling()
    
    def create_session_card(self, parent, title="Study Item", with_timer=True):
        """Create a styled study session card"""
        card = ttk.LabelFrame(
            parent, 
            text=title
        )
        
        # Add styling
        card.configure(padding=10)
        
        # Add timer if requested
        if with_timer:
            timer_var = tk.StringVar(value="Time: 0:00")
            timer_label = ttk.Label(
                card,
                textvariable=timer_var,
                font=(self.fonts["secondary"][0], 14)
            )
            timer_label.pack(side=tk.TOP, anchor=tk.E)
            
            # Make timer variable accessible
            card.timer_var = timer_var
        
        return card
    
    def create_button(self, parent, text, command=None, style="primary"):
        """Create a styled button"""
        button_styles = {
            "primary": {
                "bg": self.colors["primary"],
                "fg": "#FFFFFF",
            },
            "secondary": {
                "bg": self.colors["secondary"],
                "fg": "#FFFFFF",
            },
            "neutral": {
                "bg": self.colors["surface"],
                "fg": self.colors["text_primary"],
            }
        }
        
        chosen_style = button_styles.get(style, button_styles["primary"])
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=chosen_style["bg"],
            fg=chosen_style["fg"],
            font=(self.fonts["primary"][0], 12),
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        
        # Add hover effect
        button.bind("<Enter>", lambda e: button.configure(
            bg=self.colors["secondary"] if style == "primary" else self.colors["primary"]
        ))
        button.bind("<Leave>", lambda e: button.configure(bg=chosen_style["bg"]))
        
        return button
    
    def create_progress_bar(self, parent, mode="determinate"):
        """Create a styled progress bar"""
        progress = ttk.Progressbar(
            parent,
            orient=tk.HORIZONTAL,
            mode=mode,
            length=300
        )
        
        return progress
    
    def create_text_input(self, parent, height=5, width=40, readonly=False):
        """Create a styled text input area"""
        text_frame = ttk.Frame(parent)
        
        # Create Text widget
        text_widget = tk.Text(
            text_frame,
            height=height,
            width=width,
            font=(self.fonts["secondary"][0], self.sizes["input"]["size_px"]),
            wrap=tk.WORD,
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=1
        )
        
        # Set state if readonly
        if readonly:
            text_widget.config(state=tk.DISABLED)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return text_frame, text_widget
    
    def create_feedback_canvas(self, parent, height=30):
        """Create a canvas for real-time typing feedback"""
        canvas = tk.Canvas(
            parent,
            height=height,
            bg=self.colors["surface"],
            bd=0,
            highlightthickness=0
        )
        
        return canvas
    
    def update_feedback_canvas(self, canvas, typed, expected, max_chars=50):
        """Update feedback canvas with typing match visualization"""
        # Clear canvas
        canvas.delete("all")
        
        # Calculate char width based on canvas size
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1:  # Not yet rendered
            canvas_width = 500  # Default
        
        char_width = min(20, canvas_width / max_chars)
        
        # Draw feedback
        for i, (typed_char, expected_char) in enumerate(zip(typed, expected)):
            if i >= max_chars:  # Only show limited characters
                break
                
            # Determine color based on match
            if typed_char == expected_char:
                color = "#4CAF50"  # Green
            else:
                color = "#F44336"  # Red
            
            # Draw rectangle
            canvas.create_rectangle(
                i * char_width, 0, 
                (i + 1) * char_width, 20, 
                fill=color, 
                outline=""
            )
        
        # Show remaining characters as empty
        for i in range(len(typed), min(len(expected), max_chars)):
            canvas.create_rectangle(
                i * char_width, 0, 
                (i + 1) * char_width, 20, 
                fill=self.colors["surface"], 
                outline="#CCCCCC"
            )
        
        # Calculate accuracy percentage
        if expected:
            matches = sum(1 for a, b in zip(typed, expected) if a == b)
            accuracy = matches / min(len(typed), len(expected)) if len(typed) > 0 else 0
            
            # Draw accuracy indicator
            canvas.create_text(
                canvas_width - 50, 10,
                text=f"{accuracy*100:.0f}%",
                fill=self.colors["text_primary"],
                font=(self.fonts["secondary"][0], 10)
            )
    
    def create_sparkline(self, parent, data=None, width=200, height=30):
        """Create a sparkline visualization for typing speed trends"""
        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=self.colors["surface"],
            bd=0,
            highlightthickness=0
        )
        
        # Initialize with empty data if none provided
        if data is None:
            data = []
        
        # Draw sparkline
        self.update_sparkline(canvas, data)
        
        return canvas
    
    def update_sparkline(self, canvas, data):
        """Update sparkline with new data"""
        # Clear canvas
        canvas.delete("all")
        
        if not data:
            return
        
        # Get canvas dimensions
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:  # Not yet rendered
            width = 200  # Default
            height = 30
        
        # Normalize data
        min_val = min(data)
        max_val = max(data)
        range_val = max(max_val - min_val, 1)  # Avoid division by zero
        
        # Calculate points
        points = []
        for i, val in enumerate(data):
            x = i * (width / (len(data) - 1)) if len(data) > 1 else width / 2
            y = height - ((val - min_val) / range_val * height * 0.8 + height * 0.1)
            points.append((x, y))
        
        # Draw line
        if len(points) > 1:
            for i in range(len(points) - 1):
                canvas.create_line(
                    points[i][0], points[i][1],
                    points[i+1][0], points[i+1][1],
                    fill=self.colors["primary"],
                    width=2,
                    smooth=True
                )
        
        # Draw dots
        for x, y in points:
            canvas.create_oval(
                x-2, y-2, x+2, y+2,
                fill=self.colors["secondary"],
                outline=""
            )
        
        # Add min/max labels
        if len(data) > 0:
            canvas.create_text(
                5, 5,
                text=f"{max_val}",
                anchor=tk.NW,
                fill=self.colors["text_secondary"],
                font=(self.fonts["secondary"][0], 8)
            )
            
            canvas.create_text(
                5, height - 5,
                text=f"{min_val}",
                anchor=tk.SW,
                fill=self.colors["text_secondary"],
                font=(self.fonts["secondary"][0], 8)
            )
    
    def create_toast_notification(self, message, duration=2000):
        """Create and show a toast notification"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        
        # Calculate position (bottom right)
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        toast_width = 300
        toast_height = 50
        
        x = root_x + root_width - toast_width - 20
        y = root_y + root_height - toast_height - 20
        
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        
        # Create content
        frame = tk.Frame(
            toast,
            bg=self.colors["surface"],
            bd=1,
            relief=tk.RAISED
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(
            frame,
            text=message,
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
            font=(self.fonts["primary"][0], 12),
            padx=10,
            pady=10
        )
        label.pack(fill=tk.BOTH, expand=True)
        
        # Animate appearance
        toast.attributes("-alpha", 0.0)
        
        def fade_in():
            alpha = toast.attributes("-alpha")
            if alpha < 0.9:
                toast.attributes("-alpha", alpha + 0.1)
                toast.after(20, fade_in)
        
        def fade_out():
            alpha = toast.attributes("-alpha")
            if alpha > 0.1:
                toast.attributes("-alpha", alpha - 0.1)
                toast.after(20, fade_out)
            else:
                toast.destroy()
        
        # Start animation
        fade_in()
        
        # Schedule fade out and destroy
        toast.after(duration, fade_out)
        
        return toast


if __name__ == "__main__":
    # Test the design system
    root = tk.Tk()
    root.title("Design System Test")
    root.geometry("800x600")
    
    design = TypingStudyDesignSystem(root)
    
    # Create some test widgets
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    ttk.Label(frame, text="Typing Study Design System", style="Heading.TLabel").pack(pady=10)
    
    theme_toggle = design.create_theme_toggle(frame)
    theme_toggle.pack(pady=10)
    
    # Test buttons
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)
    
    design.create_button(button_frame, "Primary Button", style="primary").pack(side=tk.LEFT, padx=5)
    design.create_button(button_frame, "Secondary Button", style="secondary").pack(side=tk.LEFT, padx=5)
    design.create_button(button_frame, "Neutral Button", style="neutral").pack(side=tk.LEFT, padx=5)
    
    # Test card
    card = design.create_session_card(frame, "Study Card Test")
    card.pack(fill=tk.X, pady=10)
    
    # Test text input
    input_frame, text_input = design.create_text_input(card, height=3)
    input_frame.pack(fill=tk.X, pady=10)
    
    # Test feedback canvas
    feedback_canvas = design.create_feedback_canvas(card)
    feedback_canvas.pack(fill=tk.X, pady=10)
    
    # Update feedback when typing
    def update_feedback(event):
        typed = text_input.get("1.0", tk.END).strip()
        expected = "This is a test of the typing feedback system."
        design.update_feedback_canvas(feedback_canvas, typed, expected)
    
    text_input.bind("<KeyRelease>", update_feedback)
    
    # Test sparkline
    sparkline = design.create_sparkline(card, [10, 15, 12, 20, 18, 25, 22])
    sparkline.pack(fill=tk.X, pady=10)
    
    # Test toast notification
    ttk.Button(
        frame, 
        text="Show Toast", 
        command=lambda: design.create_toast_notification("Achievement unlocked: 50 WPM!")
    ).pack(pady=10)
    
    root.mainloop()