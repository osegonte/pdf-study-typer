# integration/sequential_practice_ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Callable, Optional, List, Dict, Any
import os

from parser.study_item import StudyItem, StudyItemCollection
from integration.sequential_practice import SequentialPractice


class SequentialPracticeUI:
    """User interface for sequential practice mode"""
    
    def __init__(self, parent, master_app):
        self.parent = parent
        self.master_app = master_app  # Reference to main application for accessing shared resources
        
        # Initialize components
        self.practice = SequentialPractice()
        self.current_challenge = None
        self._create_ui()
    
    def _create_ui(self):
        """Create the sequential practice UI"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with controls
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Sequential Practice Mode", 
                  font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Progress indicator
        self.progress_var = tk.StringVar(value="Progress: 0/0")
        ttk.Label(header_frame, textvariable=self.progress_var, 
                  font=("Arial", 10)).pack(side=tk.RIGHT)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.main_frame, text="Practice Options")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Source selection
        source_frame = ttk.Frame(options_frame)
        source_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(source_frame, text="Source:").pack(side=tk.LEFT)
        
        self.source_var = tk.StringVar(value="current")
        ttk.Radiobutton(source_frame, text="Current Study Items", 
                      variable=self.source_var, value="current").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(source_frame, text="Select PDF/Text", 
                      variable=self.source_var, value="select").pack(side=tk.LEFT, padx=5)
        
        # Shuffle option
        self.shuffle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Shuffle Items", 
                      variable=self.shuffle_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # Start button
        ttk.Button(options_frame, text="Start Practice", 
                 command=self._start_practice).pack(padx=10, pady=10)
        
        # Create card stack for practice items
        self.practice_area = ttk.Frame(self.main_frame)
        self.practice_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initialize card (hidden initially)
        self._create_practice_card()
        self.practice_area.pack_forget()  # Hide until practice starts
        
        # Results area
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Session Results")
        self.results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Session stats
        stats_frame = ttk.Frame(self.results_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Stats variables
        self.items_completed_var = tk.StringVar(value="Items Completed: 0")
        self.accuracy_var = tk.StringVar(value="Average Accuracy: 0%")
        self.speed_var = tk.StringVar(value="Average Speed: 0 WPM")
        self.time_var = tk.StringVar(value="Time Elapsed: 0:00")
        
        ttk.Label(stats_frame, textvariable=self.items_completed_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, textvariable=self.accuracy_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, textvariable=self.speed_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, textvariable=self.time_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Hide results initially
        self.results_frame.pack_forget()
    
    def _create_practice_card(self):
        """Create the card UI for practice items"""
        # Card frame
        self.card_frame = ttk.LabelFrame(self.practice_area, text="Practice Item")
        self.card_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Context and item type
        self.context_var = tk.StringVar()
        ttk.Label(self.card_frame, textvariable=self.context_var, 
                 font=("Arial", 10, "italic")).pack(anchor=tk.W, padx=10, pady=5)
        
        # Prompt
        self.prompt_var = tk.StringVar()
        ttk.Label(self.card_frame, textvariable=self.prompt_var, 
                 font=("Arial", 12, "bold"), wraplength=800).pack(padx=10, pady=10)
        
        # Reference text (what to type)
        reference_frame = ttk.LabelFrame(self.card_frame, text="Reference Text (Type This)")
        reference_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.reference_text = tk.Text(reference_frame, wrap=tk.WORD, height=5, 
                                     font=("Courier", 12))
        self.reference_text.pack(fill=tk.BOTH, padx=10, pady=10)
        self.reference_text.config(state=tk.DISABLED)  # Read-only
        
        # Typing area
        typing_frame = ttk.LabelFrame(self.card_frame, text="Your Answer")
        typing_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.typing_text = tk.Text(typing_frame, wrap=tk.WORD, height=5, 
                                  font=("Courier", 12))
        self.typing_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Real-time feedback (character matching)
        self.feedback_canvas = tk.Canvas(typing_frame, height=30)
        self.feedback_canvas.pack(fill=tk.X, padx=10, pady=5)
        
        # Bind key events for real-time feedback
        self.typing_text.bind("<KeyRelease>", self._update_typing_feedback)
        
        # Item results
        self.item_results_frame = ttk.Frame(self.card_frame)
        self.item_results_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Item results variables
        self.item_accuracy_var = tk.StringVar(value="Accuracy: 0%")
        self.item_wpm_var = tk.StringVar(value="WPM: 0")
        self.item_time_var = tk.StringVar(value="Time: 0s")
        
        ttk.Label(self.item_results_frame, text="Accuracy:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.item_results_frame, textvariable=self.item_accuracy_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.item_results_frame, text="Typing Speed:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.item_results_frame, textvariable=self.item_wpm_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.item_results_frame, text="Time Taken:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.item_results_frame, textvariable=self.item_time_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Control buttons
        buttons_frame = ttk.Frame(self.card_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.submit_btn = ttk.Button(buttons_frame, text="Submit", 
                                    command=self._submit_answer)
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(buttons_frame, text="Next", 
                                  command=self._next_item, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.prev_btn = ttk.Button(buttons_frame, text="Previous", 
                                  command=self._prev_item, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.skip_btn = ttk.Button(buttons_frame, text="Skip", 
                                  command=self._skip_item)
        self.skip_btn.pack(side=tk.LEFT, padx=5)
        
        self.end_btn = ttk.Button(buttons_frame, text="End Session", 
                                 command=self._end_practice)
        self.end_btn.pack(side=tk.RIGHT, padx=5)
    
    def _start_practice(self):
        """Start a sequential practice session"""
        # Get practice source
        source = self.source_var.get()
        
        if source == "current":
            # Use currently loaded study items
            if not self.master_app.study_items:
                messagebox.showinfo("No Study Items", "No study items are currently loaded. Please load some items first.")
                return
            
            self.practice = SequentialPractice(self.master_app.study_items)
        else:
            # Select a new source file
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select File for Practice",
                filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Process the selected file
            if file_path.lower().endswith(".pdf"):
                # PDF file
                from parser.content_parser import PDFStudyExtractor
                extractor = PDFStudyExtractor(file_path)
                extractor.process()
                items = extractor.get_study_items()
            elif file_path.lower().endswith(".txt"):
                # Text file
                from parser.text_parser import TextParser
                parser = TextParser.from_file(file_path)
                parser.parse()
                items = parser.get_study_items()
            else:
                messagebox.showinfo("Unsupported File", "The selected file format is not supported.")
                return
            
            if not items:
                messagebox.showinfo("No Items Found", "No study items could be extracted from the file.")
                return
            
            self.practice = SequentialPractice(items)
        
        # Check if shuffle is enabled
        if self.shuffle_var.get():
            self.practice.shuffle_remaining()
        
        # Start practice session
        self.practice.start_session()
        
        # Update UI for practice mode
        self.practice_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Load first item
        self._load_next_item()
        
        # Start timer thread
        self._start_timer()
    
    def _start_timer(self):
        """Start a timer thread to update elapsed time"""
        self.timer_running = True
        
        def update_timer():
            while self.timer_running:
                if self.practice.start_time:
                    elapsed = (datetime.now() - self.practice.start_time).total_seconds()
                    minutes, seconds = divmod(int(elapsed), 60)
                    self.time_var.set(f"Time Elapsed: {minutes}:{seconds:02d}")
                time.sleep(1)
        
        threading.Thread(target=update_timer, daemon=True).start()
    
    def _load_next_item(self):
        """Load the next practice item"""
        item = self.practice.get_next_item()
        
        if not item:
            messagebox.showinfo("Practice Complete", "You've completed all practice items!")
            self._end_practice()
            return
        
        # Update progress indicator
        current, total = self.practice.peek_progress()
        self.progress_var.set(f"Progress: {current}/{total}")
        
        # Create a challenge for this item
        self.current_challenge = self.practice.get_challenge_for_current_item()
        
        # Update UI
        self.context_var.set(f"Context: {item.context} • Type: {item.item_type.value}")
        self.prompt_var.set(item.prompt)
        
        # Set reference text
        self.reference_text.config(state=tk.NORMAL)
        self.reference_text.delete("1.0", tk.END)
        self.reference_text.insert(tk.END, item.answer)
        self.reference_text.config(state=tk.DISABLED)
        
        # Clear typing area
        self.typing_text.delete("1.0", tk.END)
        
        # Reset results
        self.item_accuracy_var.set("Accuracy: 0%")
        self.item_wpm_var.set("WPM: 0")
        self.item_time_var.set("Time: 0s")
        
        # Enable/disable buttons
        self.submit_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.NORMAL if current > 1 else tk.DISABLED)
        self.skip_btn.config(state=tk.NORMAL)
        
        # Focus on typing area
        self.typing_text.focus_set()
    
    def _update_typing_feedback(self, event):
        """Update real-time feedback for typing"""
        if not self.current_challenge:
            return
        
        # Get typed text and expected text
        typed = self.typing_text.get("1.0", tk.END).strip()
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
        """Submit the current answer"""
        if not self.current_challenge:
            return
        
        # Get typed text
        typed = self.typing_text.get("1.0", tk.END).strip()
        
        # Complete the challenge
        results = self.current_challenge.complete(typed)
        
        # Update item results display
        self.item_accuracy_var.set(f"Accuracy: {results['accuracy']*100:.1f}%")
        self.item_wpm_var.set(f"WPM: {results['wpm']:.1f}")
        self.item_time_var.set(f"Time: {results['time_taken']:.1f}s")
        
        # Record results
        self.practice.record_result(results)
        
        # Update session results
        self._update_session_results()
        
        # Update UI state
        self.submit_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
        self.skip_btn.config(state=tk.DISABLED)
    
    def _update_session_results(self):
        """Update the session results display"""
        results = self.practice.get_results()
        if not results:
            return
        
        # Calculate stats
        items_completed = len(results)
        avg_accuracy = sum(r.get("accuracy", 0) for r in results) / items_completed
        avg_wpm = sum(r.get("wpm", 0) for r in results) / items_completed
        
        # Update display
        self.items_completed_var.set(f"Items Completed: {items_completed}")
        self.accuracy_var.set(f"Average Accuracy: {avg_accuracy*100:.1f}%")
        self.speed_var.set(f"Average Speed: {avg_wpm:.1f} WPM")
    
    def _next_item(self):
        """Move to the next item"""
        self._load_next_item()
    
    def _prev_item(self):
        """Go back to the previous item"""
        item = self.practice.go_back()
        
        if item:
            # Update progress indicator
            current, total = self.practice.peek_progress()
            self.progress_var.set(f"Progress: {current}/{total}")
            
            # Create a challenge for this item
            self.current_challenge = self.practice.get_challenge_for_current_item()
            
            # Update UI
            self.context_var.set(f"Context: {item.context} • Type: {item.item_type.value}")
            self.prompt_var.set(item.prompt)
            
            # Set reference text
            self.reference_text.config(state=tk.NORMAL)
            self.reference_text.delete("1.0", tk.END)
            self.reference_text.insert(tk.END, item.answer)
            self.reference_text.config(state=tk.DISABLED)
            
            # Clear typing area
            self.typing_text.delete("1.0", tk.END)
            
            # Reset results
            self.item_accuracy_var.set("Accuracy: 0%")
            self.item_wpm_var.set("WPM: 0")
            self.item_time_var.set("Time: 0s")
            
            # Enable/disable buttons
            self.submit_btn.config(state=tk.NORMAL)
            self.next_btn.config(state=tk.DISABLED)
            self.prev_btn.config(state=tk.NORMAL if current > 1 else tk.DISABLED)
            self.skip_btn.config(state=tk.NORMAL)
            
            # Focus on typing area
            self.typing_text.focus_set()
    
    def _skip_item(self):
        """Skip the current item"""
        # Mark as skipped in some way if needed
        self.practice.skip_item()
        
        # Load next item
        self._load_next_item()
    
    def _end_practice(self):
        """End the practice session"""
        # Stop timer
        self.timer_running = False
        
        # Get session summary
        summary = self.practice.end_session()
        
        # Save results to learning tracker if available
        if hasattr(self.master_app, 'learning_tracker'):
            # Transfer relevant results to the learning tracker
            for result in self.practice.get_results():
                self.master_app.learning_tracker.record_challenge_result(result)
            
            # Update statistics
            if hasattr(self.master_app, '_update_statistics'):
                self.master_app._update_statistics()
        
        # Show summary
        messagebox.showinfo("Session Summary", 
                         f"Practice session completed!\n\n"
                         f"Items completed: {summary['items_completed']}\n"
                         f"Completion percentage: {summary['completion_percentage']:.1f}%\n"
                         f"Average accuracy: {summary['average_accuracy']*100:.1f}%\n"
                         f"Average typing speed: {summary['average_wpm']:.1f} WPM\n"
                         f"Duration: {summary['duration_minutes']:.1f} minutes")
        
        # Reset UI
        self.practice_area.pack_forget()
        self.results_frame.pack_forget()
        
        # Add to session history if possible
        if hasattr(self.master_app, 'sessions_table'):
            self.master_app.sessions_table.insert("", 0, values=(
                summary["date"],
                f"{summary['duration_minutes']:.1f} min",
                summary["items_completed"],
                f"{summary['average_accuracy']*100:.1f}%",
                f"{summary['average_wpm']:.1f}"
            ))
    
    def get_tab_frame(self):
        """Return the main frame for this tab"""
        return self.main_frame