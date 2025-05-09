# direct_practice_module.py

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from datetime import datetime
import time
from typing import List, Dict, Any, Optional, Callable

from parser.study_item import StudyItem, StudyItemCollection, StudyItemType
from parser.content_parser import PDFStudyExtractor
from parser.text_parser import TextParser
from integration.sequential_practice import SequentialPractice
from integration.challenge_generator import TypingChallenge


class DirectPracticeModule:
    """Module for direct practice with uploaded content"""
    
    def __init__(self, parent, master_app):
        self.parent = parent
        self.master_app = master_app
        
        # Initialize components
        self.practice = SequentialPractice()
        self.current_challenge = None
        self.timer_running = False
        self.start_time = None
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the direct practice UI"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Landing page header
        self._create_landing_header()
        
        # Content upload section
        self._create_upload_section()
        
        # Practice area (initially hidden)
        self._create_practice_area()
        self.practice_area.pack_forget()  # Hide until content is uploaded
        
        # Results area (initially hidden)
        self._create_results_area()
        self.results_frame.pack_forget()  # Hide until practice starts
    
    def _create_landing_header(self):
        """Create the landing page header with app description"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header_frame, 
                 text="Practice Typing with Your Study Material", 
                 font=("Arial", 24, "bold")).pack(anchor=tk.CENTER)
        
        # Description text from user requirements
        description = (
            "An optimal typing‐study session with this app would blend focused content review, deliberate practice "
            "on weak spots, real‐time feedback, and built-in spacing to maximize both retention of the material and your raw speed."
        )
        
        desc_label = ttk.Label(header_frame, text=description, 
                              wraplength=800, justify=tk.CENTER,
                              font=("Arial", 12))
        desc_label.pack(pady=10)
    
    def _create_upload_section(self):
        """Create the content upload section"""
        upload_frame = ttk.LabelFrame(self.main_frame, text="Upload Your Study Material")
        upload_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Upload options
        options_frame = ttk.Frame(upload_frame)
        options_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # PDF upload button
        pdf_frame = ttk.Frame(options_frame)
        pdf_frame.pack(side=tk.LEFT, padx=20, expand=True)
        
        pdf_icon_label = ttk.Label(pdf_frame, text="📄", font=("Arial", 24))
        pdf_icon_label.pack(pady=5)
        
        ttk.Button(pdf_frame, text="Upload PDF", 
                  command=self._upload_pdf,
                  width=20).pack(pady=5)
        
        # Text upload button
        text_frame = ttk.Frame(options_frame)
        text_frame.pack(side=tk.LEFT, padx=20, expand=True)
        
        text_icon_label = ttk.Label(text_frame, text="📝", font=("Arial", 24))
        text_icon_label.pack(pady=5)
        
        ttk.Button(text_frame, text="Upload Text File", 
                  command=self._upload_text,
                  width=20).pack(pady=5)
        
        # Paste text area
        paste_frame = ttk.LabelFrame(upload_frame, text="Or Paste Text Here")
        paste_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        self.paste_text = tk.Text(paste_frame, height=6, wrap=tk.WORD)
        self.paste_text.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        
        paste_buttons = ttk.Frame(paste_frame)
        paste_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(paste_buttons, text="Practice with Pasted Text", 
                  command=self._practice_pasted_text).pack(side=tk.RIGHT)
    
    def _create_practice_area(self):
        """Create the practice area UI"""
        self.practice_area = ttk.Frame(self.main_frame)
        self.practice_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Practice header with progress info
        practice_header = ttk.Frame(self.practice_area)
        practice_header.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.StringVar(value="Progress: 0/0")
        ttk.Label(practice_header, textvariable=self.progress_var, 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        self.time_var = tk.StringVar(value="Time: 0:00")
        ttk.Label(practice_header, textvariable=self.time_var,
                 font=("Arial", 12)).pack(side=tk.RIGHT)
        
        # Practice card
        self.card_frame = ttk.LabelFrame(self.practice_area, text="Practice Item")
        self.card_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Context
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
    
    def _create_results_area(self):
        """Create the results area"""
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Session Results")
        self.results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Session stats
        stats_frame = ttk.Frame(self.results_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Stats variables
        self.items_completed_var = tk.StringVar(value="Items Completed: 0")
        self.accuracy_var = tk.StringVar(value="Average Accuracy: 0%")
        self.speed_var = tk.StringVar(value="Average Speed: 0 WPM")
        self.session_time_var = tk.StringVar(value="Session Time: 0:00")
        
        ttk.Label(stats_frame, textvariable=self.items_completed_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, textvariable=self.accuracy_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, textvariable=self.speed_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, textvariable=self.session_time_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
    
    def _upload_pdf(self):
        """Upload and process a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if not file_path:
            return
        
        # Show progress dialog
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Processing PDF")
        progress_window.geometry("400x150")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Extracting content from PDF...",
                 font=("Arial", 12)).pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        status_var = tk.StringVar(value="Reading PDF...")
        ttk.Label(progress_window, textvariable=status_var).pack(pady=10)
        
        # Process in a separate thread to avoid freezing the UI
        def process_pdf():
            try:
                # Extract study items
                extractor = PDFStudyExtractor(file_path)
                extractor.process()
                study_items = extractor.get_study_items()
                
                # Set up practice session
                self._setup_practice_session(study_items)
                
                # Update status
                status_var.set(f"Extracted {len(study_items)} practice items")
                
                # Close progress window after a delay
                self.parent.after(1000, progress_window.destroy)
                
                # Start practice session
                self.parent.after(1200, self._start_practice_session)
                
            except Exception as e:
                status_var.set(f"Error: {str(e)}")
                self.parent.after(2000, progress_window.destroy)
                messagebox.showerror("Error", f"Failed to process PDF: {str(e)}")
        
        # Start processing thread
        threading.Thread(target=process_pdf).start()
    
    def _upload_text(self):
        """Upload and process a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Use TextParser to extract content
            parser = TextParser.from_file(file_path)
            parser.parse()
            study_items = parser.get_study_items()
            
            if not study_items:
                messagebox.showinfo("No Content Found", 
                                  "No practice content could be extracted from the file.")
                return
            
            # Set up practice session
            self._setup_practice_session(study_items)
            
            # Start practice session
            self._start_practice_session()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process text file: {str(e)}")
    
    def _practice_pasted_text(self):
        """Process pasted text and start practice"""
        text = self.paste_text.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showinfo("No Text", "Please paste some text to practice with.")
            return
        
        # Parse the text content
        parser = TextParser(text)
        parser.parse()
        study_items = parser.get_study_items()
        
        if not study_items:
            messagebox.showinfo("No Content Found", 
                              "No practice content could be extracted from the text.")
            return
        
        # Set up practice session
        self._setup_practice_session(study_items)
        
        # Start practice session
        self._start_practice_session()
    
    def _setup_practice_session(self, study_items: List[StudyItem]):
        """Set up a new practice session with the provided study items"""
        # Initialize the practice session
        self.practice = SequentialPractice(study_items)
        
        # Make study items available to the master app if needed
        if hasattr(self.master_app, 'study_items'):
            self.master_app.study_items = study_items
        
        if hasattr(self.master_app, 'study_collection'):
            collection = StudyItemCollection()
            collection.add_items(study_items)
            self.master_app.study_collection = collection
        
        # Update learning tracker if it exists
        if hasattr(self.master_app, 'learning_tracker'):
            self.master_app.learning_tracker.load_study_items(study_items)
    
    def _start_practice_session(self):
        """Start the practice session"""
        # Start the practice session
        self.practice.start_session()
        self.start_time = datetime.now()
        
        # Hide upload section and show practice area
        for child in self.main_frame.winfo_children():
            child.pack_forget()
        
        # Show practice area and results frame
        self.practice_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Load first item
        self._load_next_item()
        
        # Start timer
        self._start_timer()
    
    def _start_timer(self):
        """Start a timer to track session duration"""
        self.timer_running = True
        
        def update_timer():
            while self.timer_running:
                if self.start_time:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    minutes, seconds = divmod(int(elapsed), 60)
                    
                    # Update timer display
                    self.time_var.set(f"Time: {minutes}:{seconds:02d}")
                    self.session_time_var.set(f"Session Time: {minutes}:{seconds:02d}")
                
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
        
        # Add to session history if possible
        if hasattr(self.master_app, 'sessions_table'):
            self.master_app.sessions_table.insert("", 0, values=(
                summary["date"],
                f"{summary['duration_minutes']:.1f} min",
                summary["items_completed"],
                f"{summary['average_accuracy']*100:.1f}%",
                f"{summary['average_wpm']:.1f}"
            ))
        
        # Reset UI - show upload options again
        self.practice_area.pack_forget()
        self.results_frame.pack_forget()
        
        # Recreate the landing page
        self._create_landing_header()
        self._create_upload_section()
    
    def get_frame(self):
        """Return the main frame for this module"""
        return self.main_frame