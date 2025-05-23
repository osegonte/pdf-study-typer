import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
import threading
import time
import uuid  
from integration.sequential_practice_ui import SequentialPracticeUI
from direct_practice_module import DirectPracticeModule
from design_system import TypingStudyDesignSystem
from session_manager import StudySessionManager
# Add the current directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import your modules
try:
    from parser.text_parser import TextParser
    from parser.content_parser import PDFStudyExtractor
    from parser.study_item import StudyItem, StudyItemCollection, StudyItemType
    from integration.challenge_generator import ChallengeGenerator, TypingChallenge
    from integration.learning_tracker import LearningTracker
    from integration.study_formatter import StudyFormatter
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current Python path: {sys.path}")
    print(f"Current directory: {current_dir}")
    print(f"Directory contents: {os.listdir(current_dir)}")
    if os.path.exists(os.path.join(current_dir, 'integration')):
        print(f"Integration directory contents: {os.listdir(os.path.join(current_dir, 'integration'))}")
    if os.path.exists(os.path.join(current_dir, 'parser')):
        print(f"Parser directory contents: {os.listdir(os.path.join(current_dir, 'parser'))}")
    sys.exit(1)

class PDFStudyTypingTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Study Typing Trainer")
        self.root.geometry("900x700")
        self.design_system = TypingStudyDesignSystem(self.root)
    
        # Initialize design system
        self.design_system = TypingStudyDesignSystem(self.root)
    
        self.study_items = []
        self.study_collection = StudyItemCollection()
        self.challenge_generator = ChallengeGenerator()
        self.learning_tracker = LearningTracker()
        self.study_formatter = StudyFormatter()
        self.current_challenge = None
    
        # Streak tracking (optional for now)
        self.streak_days = 0
    
        # Data directories
        self.data_dir = os.path.join(current_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
    
        # Create UI
        self._create_ui()
      
        # Load previous progress if available
        self._try_load_progress()
    
    def _create_ui(self):
        """Create the application UI"""
        # Create a simple frame to hold the UI
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a toggle for web UI vs native UI
        self.use_web_ui = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.main_frame, text="Use Web UI", 
                       variable=self.use_web_ui, 
                       command=self._toggle_ui).pack()

        # Create the direct practice module
        self.direct_practice = DirectPracticeModule(self.main_frame, self)
    
    def _toggle_ui(self):
        """Toggle between native and web UI"""
        if self.use_web_ui.get():
           self._launch_web_ui()
        else:
            # Clear the frame
            for child in self.main_frame.winfo_children():
                child.pack_forget()
        
            # Create the direct practice module
            self.direct_practice = DirectPracticeModule(self.main_frame, self)
    
    def _create_web_ui(self):
        """Create a web-based UI using embedded browser frame"""
        import tkinter.messagebox as messagebox
    
        # Display message that web UI is not yet implemented
        messagebox.showinfo("Web UI", "Web UI is not yet implemented. Using native UI instead.")
    
        # Fall back to direct practice module
        self.direct_practice = DirectPracticeModule(self.main_frame, self)

    def _launch_web_ui(self):
        """Launch the web-based UI"""
        from api_server import launch_web_ui
        import threading
        import subprocess
        import sys
        import threading
        from api_server import run_server
    
        # Use subprocess to run the Flask server as a separate process
        flask_process = subprocess.Popen([
            sys.executable,
            'api_server.py'
        ])
    
        # Store the process reference to terminate it when needed
        self.flask_process = flask_process
        self.flask_thread = threading.Thread(target=run_server, daemon=True)
        self.flask_thread.start()

      
    # You might need a method to stop the process when closing your app
        def cleanup():
            if hasattr(self, 'flask_process'):
               self.flask_process.terminate()
    
    # Attach cleanup to window close event if using Tkinter
        self.root.protocol("WM_DELETE_WINDOW", cleanup)
    
    
    def _start_structured_session(self):
        """Start a structured 20-minute study session"""
        if not self.study_items:
            messagebox.showinfo("No Study Items", "No study items to study.")
            return
    
        # Switch to structured session tab
        for i in range(self.notebook.index("end")):
            if "20-Min Session" in self.notebook.tab(i, "text"):
                self.notebook.select(i)
                break
    
        # Start session
        self.session_manager._start_session()
    
    def _setup_structured_session_tab(self):
        """Set up the structured 20-minute session tab"""
        # Create session manager in the structured tab
        self.session_manager = StudySessionManager(self.structured_tab, self, self.design_system)
    
    def _setup_home_tab(self):
        """Set up the new home tab with direct practice module"""
        # Create and initialize the direct practice module
        self.direct_practice = DirectPracticeModule(self.home_tab, self)
            
        # Add description text at the bottom
        bottom_frame = ttk.Frame(self.home_tab)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)

        # Add feature steps from the requirements
        step_text = (
            "An optimal typing‐study session with this app would blend focused content review, "
            "deliberate practice on weak spots, real‐time feedback, and built-in spacing to maximize "
            "both retention of the material and your raw speed."
        )
        ttk.Label(bottom_frame, text=step_text, wraplength=800, justify=tk.LEFT).pack(pady=10)
    

    
    def _setup_sequential_practice(self):
        """Set up the sequential practice tab"""
        self.sequential_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sequential_tab, text="Sequential Practice")
        self.sequential_practice_ui = SequentialPracticeUI(self.sequential_tab, self)
    
   
    def _setup_dashboard(self):
        """Set up the dashboard tab"""
         # Header
        header_frame = ttk.Frame(self.dashboard_tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
    
        ttk.Label(header_frame, text="PDF Study Typing Trainer", 
                  font=("Arial", 16, "bold")).pack(side=tk.LEFT)
    
        # Main content
        content_frame = ttk.Frame(self.dashboard_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
     
        # Left panel - PDF selection and info
        left_panel = ttk.LabelFrame(content_frame, text="PDF Management")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
         # Open PDF button
        ttk.Button(left_panel, text="Open PDF", 
                   command=self._open_pdf).pack(fill=tk.X, padx=10, pady=5)
    
        # Load saved progress button
        ttk.Button(left_panel, text="Load Saved Progress", 
                   command=self._load_saved_progress).pack(fill=tk.X, padx=10, pady=5)
    
        # PDF info
        self.pdf_info_frame = ttk.LabelFrame(left_panel, text="Current PDF Information")
        self.pdf_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
        self.pdf_name_var = tk.StringVar(value="No PDF loaded")
        self.items_count_var = tk.StringVar(value="Study items: 0")
        self.extraction_date_var = tk.StringVar(value="Last extracted: N/A")
    
        ttk.Label(self.pdf_info_frame, textvariable=self.pdf_name_var).pack(anchor=tk.W, pady=2)
        ttk.Label(self.pdf_info_frame, textvariable=self.items_count_var).pack(anchor=tk.W, pady=2)
        ttk.Label(self.pdf_info_frame, textvariable=self.extraction_date_var).pack(anchor=tk.W, pady=2)
    
        # Right panel - Study info and actions
        right_panel = ttk.LabelFrame(content_frame, text="Study Management")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # Due items info
        self.due_items_var = tk.StringVar(value="Items due for review: 0")
        ttk.Label(right_panel, textvariable=self.due_items_var).pack(anchor=tk.W, padx=10, pady=5)
    
        # Overall progress
        self.mastery_var = tk.StringVar(value="Overall mastery: 0%")
        ttk.Label(right_panel, textvariable=self.mastery_var).pack(anchor=tk.W, padx=10, pady=5)
    
        # Start Study buttons
        buttons_frame = ttk.Frame(right_panel)  # This creates the buttons_frame
        buttons_frame.pack(fill=tk.X, padx=10, pady=20)
    
        # Regular study button
        self.study_btn = ttk.Button(buttons_frame, text="Start Study Session", 
                                    command=self._start_study, state=tk.DISABLED)
        self.study_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
      
        # 20-min structured session button
        self.structured_btn = ttk.Button(
            buttons_frame, 
            text="Start 20-Min Session", 
            command=self._start_structured_session
        )
        self.structured_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        self.structured_btn.config(state=tk.DISABLED)
    
        # Export options frame
        export_frame = ttk.LabelFrame(right_panel, text="Export Options")
        export_frame.pack(fill=tk.BOTH, padx=10, pady=10)
    
        ttk.Button(export_frame, text="Export to Taipo Format", 
                   command=self._export_taipo_format).pack(fill=tk.X, padx=5, pady=5)
    
        ttk.Button(export_frame, text="Export as Word List", 
                   command=self._export_word_list).pack(fill=tk.X, padx=5, pady=5) 
  
    def _setup_study_tab(self):
        """Set up the study tab"""
        # Top frame for prompt
        prompt_frame = ttk.LabelFrame(self.study_tab, text="Study Item")
        prompt_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Prompt context
        self.context_var = tk.StringVar()
        ttk.Label(prompt_frame, textvariable=self.context_var, 
                  font=("Arial", 10, "italic")).pack(anchor=tk.W, padx=10, pady=5)
        
        # Prompt text
        self.prompt_var = tk.StringVar()
        ttk.Label(prompt_frame, textvariable=self.prompt_var, 
                  font=("Arial", 12, "bold"), wraplength=800).pack(padx=10, pady=10)
        
        # Reference text (what to type)
        reference_frame = ttk.LabelFrame(self.study_tab, text="Reference Text (Type This)")
        reference_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.reference_text = tk.Text(reference_frame, wrap=tk.WORD, height=5, 
                                     font=("Courier", 12))
        self.reference_text.pack(fill=tk.BOTH, padx=10, pady=10)
        self.reference_text.config(state=tk.DISABLED)  # Read-only
        
        # Typing area
        typing_frame = ttk.LabelFrame(self.study_tab, text="Your Answer")
        typing_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.typing_text = tk.Text(typing_frame, wrap=tk.WORD, height=10, 
                                  font=("Courier", 12))
        self.typing_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Real-time feedback (character matching)
        self.feedback_canvas = tk.Canvas(typing_frame, height=30)
        self.feedback_canvas.pack(fill=tk.X, padx=10, pady=5)
        
        # Bind key events for real-time feedback
        self.typing_text.bind("<KeyRelease>", self._update_typing_feedback)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.study_tab, text="Results")
        self.results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        results_grid = ttk.Frame(self.results_frame)
        results_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Results variables
        self.accuracy_var = tk.StringVar(value="Accuracy: 0%")
        self.wpm_var = tk.StringVar(value="WPM: 0")
        self.time_var = tk.StringVar(value="Time: 0s")
        
        ttk.Label(results_grid, text="Accuracy:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(results_grid, textvariable=self.accuracy_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(results_grid, text="Typing Speed:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(results_grid, textvariable=self.wpm_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(results_grid, text="Time Taken:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(results_grid, textvariable=self.time_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.study_tab)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.submit_btn = ttk.Button(buttons_frame, text="Submit", 
                                    command=self._submit_answer, state=tk.DISABLED)
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(buttons_frame, text="Next", 
                                  command=self._next_item, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="End Session", 
                   command=self._end_study_session).pack(side=tk.RIGHT, padx=5)
    
    def _setup_stats_tab(self):
        """Set up the statistics tab"""
        # Overall statistics
        stats_frame = ttk.LabelFrame(self.stats_tab, text="Learning Statistics")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Statistics variables
        self.total_items_var = tk.StringVar(value="Total Items: 0")
        self.mastered_items_var = tk.StringVar(value="Mastered Items: 0")
        self.avg_mastery_var = tk.StringVar(value="Average Mastery: 0%")
        self.study_sessions_var = tk.StringVar(value="Study Sessions: 0")
        
        ttk.Label(stats_grid, textvariable=self.total_items_var).grid(row=0, column=0, sticky=tk.W, padx=10, pady=2)
        ttk.Label(stats_grid, textvariable=self.mastered_items_var).grid(row=1, column=0, sticky=tk.W, padx=10, pady=2)
        ttk.Label(stats_grid, textvariable=self.avg_mastery_var).grid(row=2, column=0, sticky=tk.W, padx=10, pady=2)
        ttk.Label(stats_grid, textvariable=self.study_sessions_var).grid(row=3, column=0, sticky=tk.W, padx=10, pady=2)
        
        # Progress by category
        category_frame = ttk.LabelFrame(self.stats_tab, text="Progress by Category")
        category_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a simple bar chart using canvas
        self.category_canvas = tk.Canvas(category_frame, height=200, bg="white")
        self.category_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Recent sessions
        sessions_frame = ttk.LabelFrame(self.stats_tab, text="Recent Study Sessions")
        sessions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Table for recent sessions
        columns = ("date", "duration", "items", "accuracy", "wpm")
        self.sessions_table = ttk.Treeview(sessions_frame, columns=columns, show="headings")
        
        # Configure headings
        self.sessions_table.heading("date", text="Date")
        self.sessions_table.heading("duration", text="Duration")
        self.sessions_table.heading("items", text="Items")
        self.sessions_table.heading("accuracy", text="Accuracy")
        self.sessions_table.heading("wpm", text="WPM")
        
        # Configure columns
        self.sessions_table.column("date", width=150)
        self.sessions_table.column("duration", width=100)
        self.sessions_table.column("items", width=100)
        self.sessions_table.column("accuracy", width=100)
        self.sessions_table.column("wpm", width=100)
        
        self.sessions_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export stats button
        ttk.Button(self.stats_tab, text="Export Statistics", 
                   command=self._export_statistics).pack(pady=10)
    
    def _setup_text_input_tab(self):
        """Set up the manual text input tab with improved parsing options"""
        # Main frame
        main_frame = ttk.Frame(self.text_input_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Header
        ttk.Label(main_frame, text="Add Custom Study Items", 
                font=("Arial", 16, "bold")).pack(anchor=tk.W, pady=10)
        
        ttk.Label(main_frame, text="Create your own study items for typing practice.", 
                font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        # Create notebook for sub-tabs
        input_notebook = ttk.Notebook(main_frame)
        input_notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create sub-tabs
        single_item_tab = ttk.Frame(input_notebook)
        bulk_text_tab = ttk.Frame(input_notebook)
        import_tab = ttk.Frame(input_notebook)
        
        input_notebook.add(single_item_tab, text="Single Item")
        input_notebook.add(bulk_text_tab, text="Bulk Text")
        input_notebook.add(import_tab, text="Import")
        
        # Setup Single Item tab
        self._setup_single_item_tab(single_item_tab)
        
        # Setup Bulk Text tab
        self._setup_bulk_text_tab(bulk_text_tab)
        
        # Setup Import tab
        self._setup_import_tab(import_tab)
        
        # Status bar at the bottom
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.item_count_var = tk.StringVar(value="Current items: 0")
        ttk.Label(status_frame, textvariable=self.item_count_var).pack(side=tk.LEFT)
        
        ttk.Button(status_frame, text="Start Studying", 
                command=self._start_study).pack(side=tk.RIGHT)
        
        # Save button
        ttk.Button(status_frame, text="Save Items", 
                command=self._save_custom_items).pack(side=tk.RIGHT, padx=5)
    
    def _setup_single_item_tab(self, parent):
        """Setup the single item input tab"""
        # Form for adding individual items
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Item Type
        type_frame = ttk.Frame(item_frame)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Item Type:").pack(side=tk.LEFT)
        
        self.item_type_var = tk.StringVar(value="key_concept")
        item_types = [
            ("Key Concept", "key_concept"),
            ("Definition", "definition"),
            ("Fill in Blank", "fill_in_blank"),
            ("Formula", "formula"),
            ("List", "list")
        ]
        
        type_select_frame = ttk.Frame(type_frame)
        type_select_frame.pack(side=tk.LEFT, padx=10)
        
        for text, value in item_types:
            ttk.Radiobutton(type_select_frame, text=text, value=value, 
                            variable=self.item_type_var).pack(side=tk.LEFT, padx=5)
        
        # Context
        context_frame = ttk.Frame(item_frame)
        context_frame.pack(fill=tk.X, pady=5)
        ttk.Label(context_frame, text="Context:").pack(side=tk.LEFT)
        self.context_entry = ttk.Entry(context_frame, width=40)
        self.context_entry.pack(side=tk.LEFT, padx=10)
        self.context_entry.insert(0, "Custom Content")
        
        # Importance
        importance_frame = ttk.Frame(item_frame)
        importance_frame.pack(fill=tk.X, pady=5)
        ttk.Label(importance_frame, text="Importance (1-10):").pack(side=tk.LEFT)
        self.importance_var = tk.IntVar(value=5)
        importance_scale = ttk.Scale(importance_frame, from_=1, to=10, variable=self.importance_var,
                                    orient=tk.HORIZONTAL, length=200)
        importance_scale.pack(side=tk.LEFT, padx=10)
        # Current value display
        self.importance_label = ttk.Label(importance_frame, text="5")
        self.importance_label.pack(side=tk.LEFT)
        # Update label when scale changes
        importance_scale.bind("<Motion>", lambda e: self.importance_label.config(
            text=str(self.importance_var.get())))
        
        # Prompt
        prompt_frame = ttk.LabelFrame(item_frame, text="Prompt (what the user will see)")
        prompt_frame.pack(fill=tk.X, pady=5)
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Answer
        answer_frame = ttk.LabelFrame(item_frame, text="Answer (what the user will type)")
        answer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.answer_text = tk.Text(answer_frame, height=5, wrap=tk.WORD)
        self.answer_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add button
        ttk.Button(item_frame, text="Add Item", 
                command=self._add_custom_item).pack(pady=10)

    def _setup_bulk_text_tab(self, parent):
        """Setup the bulk text input tab"""
        # Main frame
        bulk_frame = ttk.Frame(parent)
        bulk_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        instruction_frame = ttk.LabelFrame(bulk_frame, text="Instructions")
        instruction_frame.pack(fill=tk.X, pady=5)
        
        instructions = (
            "Enter text in any of these formats:\n\n"
            "1. Plain text (each line becomes an item)\n"
            "2. Q&A format (Q: question\nA: answer)\n"
            "3. Definition list (Term - Definition or Term: Definition)\n"
            "4. Bullet list (• item or - item or * item)\n"
            "5. Custom format (prompt|answer|context)"
        )
        
        ttk.Label(instruction_frame, text=instructions, justify=tk.LEFT,
                wraplength=600).pack(padx=10, pady=10)
        
        # Format options
        format_frame = ttk.Frame(bulk_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Preferred Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="auto")
        formats = [
            ("Auto-detect", "auto"),
            ("Plain Text", "plain"),
            ("Q&A", "qa"),
            ("Definitions", "definition"),
            ("List", "list"),
            ("Custom", "custom")
        ]
        
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, value=value, 
                        variable=self.format_var).pack(side=tk.LEFT, padx=5)
        
        # Text input
        text_frame = ttk.LabelFrame(bulk_frame, text="Enter Your Text")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.bulk_text = tk.Text(text_frame, wrap=tk.WORD)
        self.bulk_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sample text button
        def insert_sample():
            sample = (
                "Q: What is the capital of France?\n"
                "A: Paris\n\n"
                "Q: What is the largest planet in our solar system?\n"
                "A: Jupiter\n\n"
                "Photosynthesis - The process by which plants convert light energy into chemical energy\n\n"
                "• Item one in a list\n"
                "• Item two in a list\n"
                "• Item three in a list\n\n"
                "Prompt for custom item|Answer to be typed|Study Context"
            )
            self.bulk_text.delete("1.0", tk.END)
            self.bulk_text.insert("1.0", sample)
        
        ttk.Button(bulk_frame, text="Insert Sample Text", 
                command=insert_sample).pack(side=tk.LEFT, pady=10)
        
        # Import button
        ttk.Button(bulk_frame, text="Import Items", 
                command=self._import_bulk_items).pack(side=tk.RIGHT, pady=10)

    def _setup_import_tab(self, parent):
        """Setup the import tab"""
        # Main frame
        import_frame = ttk.Frame(parent)
        import_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File import section
        file_frame = ttk.LabelFrame(import_frame, text="Import from File")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Import study items from a text file. The file can contain:\n"
                "• Plain text with one item per line\n"
                "• Q&A format\n"
                "• Definitions\n"
                "• Lists\n", 
                justify=tk.LEFT).pack(padx=10, pady=10)
        
        ttk.Button(file_frame, text="Browse for Text File", 
                command=self._import_text_from_file).pack(padx=10, pady=10)
        
        # PDF import section (use existing functionality)
        pdf_frame = ttk.LabelFrame(import_frame, text="Import from PDF")
        pdf_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(pdf_frame, text="Import study items from a PDF document using the built-in parser.\n"
                "The parser will extract definitions, key concepts, formulas, and lists.",
                justify=tk.LEFT).pack(padx=10, pady=10)
        
        ttk.Button(pdf_frame, text="Browse for PDF File", 
                command=self._open_pdf).pack(padx=10, pady=10)
        
        # Clipboard import
        clipboard_frame = ttk.LabelFrame(import_frame, text="Import from Clipboard")
        clipboard_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(clipboard_frame, text="Import study items from the clipboard.",
                justify=tk.LEFT).pack(padx=10, pady=10)
        
        ttk.Button(clipboard_frame, text="Paste from Clipboard", 
                command=self._import_from_clipboard).pack(padx=10, pady=10)

    def _add_custom_item(self):
        """Add a custom study item from the form"""
        # Get values from form
        item_type_str = self.item_type_var.get()
        item_type = getattr(StudyItemType, item_type_str.upper())
        
        context = self.context_entry.get()
        importance = self.importance_var.get()
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        answer = self.answer_text.get("1.0", tk.END).strip()
        
        # Validate
        if not prompt or not answer:
            messagebox.showwarning("Missing Information", "Please provide both prompt and answer.")
            return
        
        # Create study item
        item = StudyItem(
            id=str(uuid.uuid4()),
            prompt=prompt,
            answer=answer,
            context=context,
            item_type=item_type,
            importance=importance,
            mastery=0.0,
            source_document="Manual Input"
        )
        
        # Add to study items
        self.study_items.append(item)
        
        # Add to collection
        if not hasattr(self, 'study_collection') or self.study_collection is None:
            self.study_collection = StudyItemCollection()
        self.study_collection.add_item(item)
        
        # Update learning tracker and challenge generator
        if not hasattr(self, 'learning_tracker') or self.learning_tracker is None:
            self.learning_tracker = LearningTracker()
        self.learning_tracker.load_study_items([item])
        
        if not hasattr(self, 'challenge_generator') or self.challenge_generator is None:
            self.challenge_generator = ChallengeGenerator(self.study_items)
        else:
            self.challenge_generator.add_items([item])
        
        # Clear form
        self.prompt_text.delete("1.0", tk.END)
        self.answer_text.delete("1.0", tk.END)
        
        # Update item count
        self.item_count_var.set(f"Current items: {len(self.study_items)}")
        
        # Enable study button if not already enabled
        self.study_btn.config(state=tk.NORMAL)
        
        # Show success message
        messagebox.showinfo("Item Added", "Study item added successfully!")
        
        # Update statistics
        self._update_statistics()

    def _import_bulk_items(self):
        """Import multiple items from bulk text input"""
        bulk_text = self.bulk_text.get("1.0", tk.END).strip()
        
        if not bulk_text:
            messagebox.showwarning("Empty Input", "Please enter some text to import.")
            return
        
        # Get preferred format
        format_preference = self.format_var.get()
        
        # Use TextParser to extract study items
        parser = TextParser(bulk_text)
        
        # If format is specified and not auto-detect, call the specific parser
        if format_preference == "qa":
            parser._parse_qa_format()
        elif format_preference == "definition":
            parser._parse_definition_list()
        elif format_preference == "list":
            parser._parse_bullet_list()
        elif format_preference == "plain":
            parser._parse_simple_lines()
        else:  # auto detect
            parser.parse()
        
        items = parser.get_study_items()
        
        if not items:
            messagebox.showinfo("No Items Found", 
                            "No study items could be extracted from the text. "
                            "Try using a different format or add items manually.")
            return
        
        # Add items to study collection
        for item in items:
            self.study_items.append(item)
            
            if not hasattr(self, 'study_collection') or self.study_collection is None:
                self.study_collection = StudyItemCollection()
            self.study_collection.add_item(item)
        
        # Update learning tracker and challenge generator
        if not hasattr(self, 'learning_tracker') or self.learning_tracker is None:
            self.learning_tracker = LearningTracker()
        self.learning_tracker.load_study_items(items)
        
        if not hasattr(self, 'challenge_generator') or self.challenge_generator is None:
            self.challenge_generator = ChallengeGenerator(self.study_items)
        else:
            self.challenge_generator.add_items(items)
        
        # Clear text area
        self.bulk_text.delete("1.0", tk.END)
        
        # Update item count
        self.item_count_var.set(f"Current items: {len(self.study_items)}")
        
        # Enable study button if we have items
        if self.study_items:
            self.study_btn.config(state=tk.NORMAL)
        
        # Show success message
        messagebox.showinfo("Items Imported", f"Successfully imported {len(items)} study items!")
        
        # Update statistics
        self._update_statistics()

    def _import_text_from_file(self):
        """Import study items from a text file using the TextParser"""
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Use TextParser to extract study items
            parser = TextParser.from_file(file_path)
            parser.parse()
            items = parser.get_study_items()
            
            if not items:
                messagebox.showinfo("No Items Found", 
                                "No study items could be extracted from the file. "
                                "Try using a different file or format.")
                return
            
            # Add items to study collection
            for item in items:
                self.study_items.append(item)
                
                if not hasattr(self, 'study_collection') or self.study_collection is None:
                    self.study_collection = StudyItemCollection()
                self.study_collection.add_item(item)
            
            # Update learning tracker and challenge generator
            if not hasattr(self, 'learning_tracker') or self.learning_tracker is None:
                self.learning_tracker = LearningTracker()
            self.learning_tracker.load_study_items(items)
            
            if not hasattr(self, 'challenge_generator') or self.challenge_generator is None:
                self.challenge_generator = ChallengeGenerator(self.study_items)
            else:
                self.challenge_generator.add_items(items)
            
            # Update UI
            self.pdf_name_var.set(f"Loaded text: {os.path.basename(file_path)}")
            self.items_count_var.set(f"Study items: {len(self.study_items)}")
            self.extraction_date_var.set(f"Loaded on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Update item count in text input tab
            self.item_count_var.set(f"Current items: {len(self.study_items)}")
            
            # Enable study button
            self.study_btn.config(state=tk.NORMAL)
            
            # Show success message
            messagebox.showinfo("Text Imported", f"Successfully imported {len(items)} study items from the text file!")
            
            # Update statistics
            self._update_statistics()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import text file: {str(e)}")

    def _import_from_clipboard(self):
        """Import text from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            
            if not clipboard_text:
                messagebox.showinfo("Empty Clipboard", "The clipboard is empty.")
                return
            
            # Insert clipboard content into bulk text
            self.bulk_text.delete("1.0", tk.END)
            self.bulk_text.insert("1.0", clipboard_text)
            
            # Switch to bulk text tab
            for i in range(self.notebook.index("end")):
                if "Add Text" in self.notebook.tab(i, "text"):
                    self.notebook.select(i)
                    break
            
            # Focus on the bulk text tab
            for child in self.text_input_tab.winfo_children():
                if isinstance(child, ttk.Notebook):
                    for i in range(child.index("end")):
                        if "Bulk Text" in child.tab(i, "text"):
                            child.select(i)
                            break
            
            messagebox.showinfo("Clipboard Content", 
                            "Clipboard content has been inserted into the bulk text area.\n"
                            "Click 'Import Items' to process and add the content.")
        
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Failed to get clipboard content: {str(e)}")

    def _save_custom_items(self):
        """Save custom study items to a file"""
        if not self.study_items:
            messagebox.showinfo("No Items", "No study items to save.")
            return
        
        # Get filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialdir=self.data_dir,
            initialfile="custom_study_items.json",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if not filename:
            return
        
        try:
            # Save study collection
            if not hasattr(self, 'study_collection') or self.study_collection is None:
                self.study_collection = StudyItemCollection()
                self.study_collection.add_items(self.study_items)
            
            self.study_collection.save_to_file(filename)
            messagebox.showinfo("Success", f"Saved {len(self.study_items)} study items to {filename}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save items: {str(e)}")
    
    def _open_pdf(self):
        """Open a PDF file for study"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if not file_path:
            return
        
        # Show progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Extracting Study Items")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Extracting study items from PDF...",
                 font=("Arial", 12)).pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        status_var = tk.StringVar(value="Initializing...")
        ttk.Label(progress_window, textvariable=status_var).pack(pady=10)
        
        # Extract in a separate thread to avoid freezing the UI
        def extract_from_pdf():
            try:
                # Update status
                status_var.set("Reading PDF...")
                self.root.update_idletasks()
                
                # Extract study items
                extractor = PDFStudyExtractor(file_path)
                
                status_var.set("Processing content...")
                self.root.update_idletasks()
                
                extractor.process()
                self.study_items = extractor.get_study_items()
                
                # Update UI with extracted info
                self.pdf_name_var.set(f"PDF: {os.path.basename(file_path)}")
                self.items_count_var.set(f"Study items: {len(self.study_items)}")
                self.extraction_date_var.set(f"Last extracted: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                # Update study collection
                self.study_collection = StudyItemCollection()
                self.study_collection.add_items(self.study_items)
                
                # Update learning tracker and challenge generator
                self.learning_tracker = LearningTracker()
                self.learning_tracker.load_study_items(self.study_items)
                self.challenge_generator = ChallengeGenerator(self.study_items)
                
                # Enable study button if we have items
                if self.study_items:
                    self.study_btn.config(state=tk.NORMAL)
                
                # Update statistics
                self._update_statistics()
                
                # Save the extracted items
                filename = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(self.data_dir, f"{filename}_study_items.json")
                self.study_collection.save_to_file(save_path)
                
                status_var.set(f"Extracted {len(self.study_items)} study items!")
            except Exception as e:
                status_var.set(f"Error: {str(e)}")
            finally:
                # Close progress window after a delay
                self.root.after(1500, progress_window.destroy)
        
        # Start extraction thread
        threading.Thread(target=extract_from_pdf).start()
    
    def _load_saved_progress(self):
        """Load saved progress from a file"""
        files = [f for f in os.listdir(self.data_dir) 
                if f.endswith("_study_items.json")]
        
        if not files:
            messagebox.showinfo("No Saved Files", "No saved study files found.")
            return
        
        # Create a dialog to select a file
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Saved Progress")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select a study file to load:",
                 font=("Arial", 12)).pack(pady=10)
        
        # Create listbox with scrollbar
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for file in files:
            listbox.insert(tk.END, file)
        
        def on_load():
            if not listbox.curselection():
                messagebox.showinfo("No Selection", "Please select a file to load.")
                return
            
            selected_file = listbox.get(listbox.curselection()[0])
            file_path = os.path.join(self.data_dir, selected_file)
            
            # Load study items
            collection = StudyItemCollection.load_from_file(file_path)
            self.study_items = collection.get_items()
            self.study_collection = collection
            
            # Update UI
            self.pdf_name_var.set(f"Loaded: {selected_file}")
            self.items_count_var.set(f"Study items: {len(self.study_items)}")
            self.extraction_date_var.set(f"Loaded on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Update learning tracker and challenge generator
            self.learning_tracker = LearningTracker()
            self.learning_tracker.load_study_items(self.study_items)
            self.challenge_generator = ChallengeGenerator(self.study_items)
            
            # Enable study button if we have items
            if self.study_items:
                self.study_btn.config(state=tk.NORMAL)
            
            # Update statistics
            self._update_statistics()
            
            dialog.destroy()
            messagebox.showinfo("Success", f"Loaded {len(self.study_items)} study items!")
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Load", command=on_load).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _export_taipo_format(self):
        """Export study items to Taipo format"""
        if not self.study_items:
            messagebox.showinfo("No Study Items", "No study items to export.")
            return
        
        # Get filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialdir=self.data_dir,
            initialfile="taipo_study_content.json",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if not filename:
            return
        
        try:
            # Export to Taipo format
            self.study_formatter.save_taipo_format(self.study_items, 
                                                  os.path.splitext(os.path.basename(filename))[0])
            messagebox.showinfo("Success", f"Exported study items to Taipo format!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _export_word_list(self):
        """Export study items as a word list"""
        if not self.study_items:
            messagebox.showinfo("No Study Items", "No study items to export.")
            return
        
        # Get filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=self.data_dir,
            initialfile="study_wordlist.jp.txt",
            filetypes=[("Text Files", "*.txt")]
        )
        
        if not filename:
            return
        
        try:
            # Export as word list
            self.study_formatter.convert_to_word_list(self.study_items, 
                                                    os.path.splitext(os.path.basename(filename))[0])
            messagebox.showinfo("Success", f"Exported study items as word list!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _export_statistics(self):
        """Export learning statistics"""
        # Get filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialdir=self.data_dir,
            initialfile="learning_statistics.json",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if not filename:
            return
        
        try:
            # Get statistics
            stats = self.learning_tracker.get_learning_stats()
            
            # Additional information
            stats["export_date"] = datetime.now().isoformat()
            stats["total_study_items"] = len(self.study_items)
            
            # Save to file
            with open(filename, "w") as f:
                import json
                json.dump(stats, f, indent=2)
            
            messagebox.showinfo("Success", f"Exported learning statistics!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _start_study(self):
        """Start a study session"""
        if not self.study_items:
            messagebox.showinfo("No Study Items", "No study items to study.")
            return
        
        # Initialize the learning tracker
        self.learning_tracker.start_session()
        
        # Load the first item
        self._load_next_item()
        
        # Switch to study tab
        self.notebook.select(1)
    
    def _load_next_item(self):
        """Load the next study item"""
        # Get the next item from learning tracker
        study_item = self.learning_tracker.get_next_item()
        
        if not study_item:
            messagebox.showinfo("No More Items", "No more items to study.")
            self._end_study_session()
            return
        
        # Generate a challenge
        self.current_challenge = self.challenge_generator.challenge_generator = TypingChallenge(study_item)
        self.current_challenge.start()
        
        # Update UI
        self.context_var.set(f"Context: {study_item.context} • Type: {study_item.item_type.value}")
        self.prompt_var.set(study_item.prompt)
        
        # Set reference text
        self.reference_text.config(state=tk.NORMAL)
        self.reference_text.delete(1.0, tk.END)
        self.reference_text.insert(tk.END, study_item.answer)
        self.reference_text.config(state=tk.DISABLED)
        
        # Clear typing area
        self.typing_text.delete(1.0, tk.END)
        
        # Reset results
        self.accuracy_var.set("Accuracy: 0%")
        self.wpm_var.set("WPM: 0")
        self.time_var.set("Time: 0s")
        
        # Enable submit button, disable next button
        self.submit_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.DISABLED)
        
        # Focus on typing area
        self.typing_text.focus_set()
    
    def _update_typing_feedback(self, event):
        """Update real-time feedback for typing"""
        if not self.current_challenge:
            return
        
        # Get typed text and expected text
        typed = self.typing_text.get(1.0, tk.END).strip()
        expected = self.current_challenge.study_item.answer
        
        # Clear canvas
        self.feedback_canvas.delete("all")
        
        # Draw feedback
        for i, (typed_char, expected_char) in enumerate(zip(typed, expected)):
            if i >= 50:  # Only show first 50 characters
                break
                
            if typed_char == expected_char:
                color = "green"
            else:
                color = "red"
            
            self.feedback_canvas.create_rectangle(
                i * 10, 0, (i + 1) * 10, 20, fill=color, outline=""
            )
    
    def _submit_answer(self):
        """Submit the answer for the current challenge"""
        if not self.current_challenge:
            return
        
        # Get typed text
        typed = self.typing_text.get(1.0, tk.END).strip()
        
        # Complete the challenge
        results = self.current_challenge.complete(typed)
        
        # Update results display
        self.accuracy_var.set(f"Accuracy: {results['accuracy']*100:.1f}%")
        self.wpm_var.set(f"WPM: {results['wpm']:.1f}")
        self.time_var.set(f"Time: {results['time_taken']:.1f}s")
        
        # Record results in learning tracker
        self.learning_tracker.record_challenge_result(results)
        
        # Update UI state
        self.submit_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
    
    def _next_item(self):
        """Move to the next study item"""
        self._load_next_item()
    
    def _end_study_session(self):
        """End the current study session"""
        if hasattr(self.learning_tracker, 'session_stats') and self.learning_tracker.session_stats["start_time"]:
            # Get session summary
            summary = self.learning_tracker.end_session()
            
            # Add to sessions table
            self.sessions_table.insert("", 0, values=(
                summary["date"],
                f"{summary['duration_minutes']:.1f} min",
                summary["items_studied"],
                f"{summary['accuracy_percentage']:.1f}%",
                f"{summary['average_wpm']:.1f}"
            ))
            
            # Save progress
            self.learning_tracker.save_progress()
            
            # Update statistics
            self._update_statistics()
            
            # Show summary
            messagebox.showinfo("Session Summary", 
                               f"Session completed!\n\n"
                               f"Items studied: {summary['items_studied']}\n"
                               f"Accuracy: {summary['accuracy_percentage']:.1f}%\n"
                               f"Average typing speed: {summary['average_wpm']:.1f} WPM\n"
                               f"Duration: {summary['duration_minutes']:.1f} minutes")
        
        # Switch back to dashboard
        self.notebook.select(0)
    
    def _update_statistics(self):
        """Update all statistics displays"""
        # Update due items count
        due_count = self.learning_tracker.get_due_items_count()
        self.due_items_var.set(f"Items due for review: {due_count}")
        
        # Update overall mastery
        stats = self.learning_tracker.get_learning_stats()
        self.mastery_var.set(f"Overall mastery: {stats['average_mastery']*100:.1f}%")
        
        # Update stats tab
        self.total_items_var.set(f"Total Items: {stats['total_items']}")
        self.mastered_items_var.set(f"Mastered Items: {stats['mastered_items']} ({stats['mastery_percentage']:.1f}%)")
        self.avg_mastery_var.set(f"Average Mastery: {stats['average_mastery']*100:.1f}%")

        # Update category progress visualization
        self._update_category_visualization()
    
    def _update_category_visualization(self):
        """Update the category progress visualization"""
        if not self.study_items:
            return
        
        # Clear canvas
        self.category_canvas.delete("all")
        
        # Group items by type
        categories = {}
        for item in self.study_items:
            category = item.item_type.value
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Calculate average mastery for each category
        mastery_by_category = {}
        for category, items in categories.items():
            avg_mastery = sum(item.mastery for item in items) / len(items)
            mastery_by_category[category] = avg_mastery
        
        # Draw bars
        canvas_width = self.category_canvas.winfo_width()
        canvas_height = self.category_canvas.winfo_height()
        
        if canvas_width <= 1:  # Not yet rendered
            canvas_width = 500  # Default width
            canvas_height = 200  # Default height
        
        bar_width = canvas_width / (len(mastery_by_category) + 1)
        max_bar_height = canvas_height - 40  # Leave space for labels
        
        # Colors for different categories
        colors = {
            "definition": "#4287f5",  # Blue
            "key_concept": "#42f551",  # Green
            "formula": "#f54242",  # Red
            "list": "#f5a742",  # Orange
            "fill_in_blank": "#b042f5"  # Purple
        }
        
        # Draw bars
        x_offset = bar_width / 2
        for category, mastery in mastery_by_category.items():
            bar_height = mastery * max_bar_height
            
            # Bar
            color = colors.get(category, "#888888")
            self.category_canvas.create_rectangle(
                x_offset, canvas_height - 30 - bar_height,
                x_offset + bar_width - 10, canvas_height - 30,
                fill=color, outline="black"
            )
            
            # Label
            self.category_canvas.create_text(
                x_offset + bar_width / 2 - 5, canvas_height - 15,
                text=category.replace("_", " ").title(),
                angle=45, anchor=tk.NE
            )
            
            # Percentage
            self.category_canvas.create_text(
                x_offset + bar_width / 2 - 5, canvas_height - 30 - bar_height - 5,
                text=f"{mastery*100:.0f}%",
                anchor=tk.S
            )
            
            x_offset += bar_width
    
    def _try_load_progress(self):
        """Try to load previous progress if available"""
        default_progress_file = os.path.join(self.data_dir, "learning_progress.json")
        
        if os.path.exists(default_progress_file):
            try:
                # Load progress
                success = self.learning_tracker.load_progress()
                
                if success:
                    # Get items from learning tracker
                    self.study_items = self.learning_tracker.spaced_repetition.study_items
                    
                    # Update study collection
                    self.study_collection = StudyItemCollection()
                    self.study_collection.add_items(self.study_items)
                    
                    # Update challenge generator
                    self.challenge_generator = ChallengeGenerator(self.study_items)
                    
                    # Update UI
                    self.pdf_name_var.set(f"Loaded from previous session")
                    self.items_count_var.set(f"Study items: {len(self.study_items)}")
                    self.extraction_date_var.set(f"Loaded on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    
                    # Enable study button if we have items
                    if self.study_items:
                        self.study_btn.config(state=tk.NORMAL)
                    
                    # Update statistics
                    self._update_statistics()
            except Exception as e:
                print(f"Error loading previous progress: {str(e)}")

    def _parse_text_input(self, text):
        """Parse various text input formats to create study items
        
        Supported formats:
        1. Q&A format: "Q: question\nA: answer"
        2. Pipe-delimited: "prompt|answer|context"
        3. Simple text: Each line becomes an item to type
        """
        items = []
        
        # Check if it's Q&A format
        if "Q:" in text and "A:" in text:
            # Split by Q: to get individual QA pairs
            qa_pairs = text.split("Q:")
            for pair in qa_pairs:
                if not pair.strip():
                    continue
                    
                # Find answer part
                if "A:" in pair:
                    question_part, answer_part = pair.split("A:", 1)
                    prompt = f"Q: {question_part.strip()}"
                    answer = answer_part.strip()
                    
                    item = StudyItem(
                        id=str(uuid.uuid4()),
                        prompt=prompt,
                        answer=answer,
                        context="Q&A",
                        item_type=StudyItemType.KEY_CONCEPT,
                        importance=self.importance_var.get(),
                        mastery=0.0,
                        source_document="Text Input"
                    )
                    items.append(item)
        else:
            # Process as simple lines or pipe-delimited
            lines = text.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                    
                if '|' in line:
                    # Pipe-delimited format
                    parts = line.split('|')
                    if len(parts) >= 3:
                        prompt, answer, context = parts[0], parts[1], parts[2]
                    elif len(parts) == 2:
                        prompt, answer = parts[0], parts[1]
                        context = "Custom Content"
                    else:
                        prompt = "Type this:"
                        answer = line
                        context = "Custom Content"
                else:
                    # Simple line format
                    prompt = "Type this:"
                    answer = line
                    context = "Custom Content"
                    
                item = StudyItem(
                    id=str(uuid.uuid4()),
                    prompt=prompt,
                    answer=answer,
                    context=context,
                    item_type=StudyItemType.KEY_CONCEPT,
                    importance=self.importance_var.get(),
                    mastery=0.0,
                    source_document="Text Input"
                )
                items.append(item)
        
        return items


def main():
    # Create root window
    root = tk.Tk()
    root.title("PDF Study Typing Trainer")
    
    # Set theme - use 'clam' theme for better aesthetics
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10))
    style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))
    
    # Create the application
    app = PDFStudyTypingTrainer(root)
    
    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
    