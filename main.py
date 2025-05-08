import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
import threading
import time

# Add the current directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import your modules
try:
    from parser.content_parser import PDFStudyExtractor
    from parser.study_item import StudyItem, StudyItemCollection
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
        
        # Initialize components
        self.study_items = []
        self.study_collection = StudyItemCollection()
        self.challenge_generator = ChallengeGenerator()
        self.learning_tracker = LearningTracker()
        self.study_formatter = StudyFormatter()
        self.current_challenge = None
        
        # Data directories
        self.data_dir = os.path.join(current_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create UI
        self._create_ui()
        
        # Load previous progress if available
        self._try_load_progress()
    
    def _create_ui(self):
        """Create the application UI"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.study_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.study_tab, text="Study")
        self.notebook.add(self.stats_tab, text="Statistics")
        
        # Set up tabs
        self._setup_dashboard()
        self._setup_study_tab()
        self._setup_stats_tab()
    
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
        
        # Start Study button
        self.study_btn = ttk.Button(right_panel, text="Start Study Session", 
                                    command=self._start_study, state=tk.DISABLED)
        self.study_btn.pack(fill=tk.X, padx=10, pady=20)
        
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