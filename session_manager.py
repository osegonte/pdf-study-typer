# session_manager.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional, Callable

from parser.study_item import StudyItem, StudyItemCollection
from integration.challenge_generator import TypingChallenge
from integration.learning_tracker import LearningTracker

class StudySessionManager:
    """
    Manages a complete study session following the ideal 20-minute flow:
    1. Warm-Up (2 min)
    2. Targeted Drills (5 min)
    3. Adaptive Challenge (5 min)
    4. Error-Focus Micro-Sessions (3 min)
    5. Review & Spaced Repetition Setup (3 min)
    6. Habit Cadence & Reminder (2 min)
    """
    
    def __init__(self, parent, master_app, design_system):
        self.parent = parent
        self.master_app = master_app
        self.design = design_system
        
        # Initialize components
        self.learning_tracker = self.master_app.learning_tracker if hasattr(self.master_app, 'learning_tracker') else LearningTracker()
        self.study_items = self.master_app.study_items if hasattr(self.master_app, 'study_items') else []
        
        # Session state
        self.session_active = False
        self.current_step = 0
        self.session_start_time = None
        self.step_start_time = None
        self.timer_running = False
        self.wpm_history = []
        self.accuracy_history = []
        self.error_items = []
        self.current_challenge = None
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the session manager UI"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header with title
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            header_frame, 
            text="Structured 20-Minute Study Session",
            style="Heading.TLabel"
        ).pack(side=tk.LEFT)
        
        # Timer display
        self.timer_var = tk.StringVar(value="Time: 0:00")
        self.timer_label = ttk.Label(
            header_frame,
            textvariable=self.timer_var,
            font=(self.design.fonts["secondary"][0], 14)
        )
        self.timer_label.pack(side=tk.RIGHT)
        
        # Progress visualization
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.step_label = ttk.Label(
            progress_frame, 
            text="Ready to Start",
            font=(self.design.fonts["primary"][0], 14, "bold")
        )
        self.step_label.pack(anchor=tk.W)
        
        self.progress_desc = ttk.Label(
            progress_frame,
            text="Follow the 20-minute structured session for optimal learning",
            wraplength=800
        )
        self.progress_desc.pack(anchor=tk.W, pady=5)
        
        # Progress indicator
        self.progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        # Session flow visualization
        flow_frame = ttk.LabelFrame(self.main_frame, text="Session Flow")
        flow_frame.pack(fill=tk.X, pady=10)
        
        # Create step indicators
        self.step_frames = []
        self.step_durations = [2, 5, 5, 3, 3, 2]  # Minutes per step
        
        steps_frame = ttk.Frame(flow_frame)
        steps_frame.pack(fill=tk.X, padx=10, pady=10)
        
        step_titles = [
            "Warm-Up", 
            "Targeted Drills", 
            "Adaptive Challenge",
            "Error-Focus",
            "Review",
            "Habit Tracking"
        ]
        
        for i, (title, duration) in enumerate(zip(step_titles, self.step_durations)):
            step_frame = ttk.Frame(steps_frame)
            step_frame.grid(row=0, column=i, padx=5)
            
            # Circle indicator
            indicator = tk.Canvas(step_frame, width=40, height=40, highlightthickness=0, bg=self.design.colors["background"])
            indicator.create_oval(5, 5, 35, 35, outline=self.design.colors["primary"], width=2, fill="")
            indicator.create_text(20, 20, text=str(i+1), fill=self.design.colors["primary"])
            indicator.pack()
            
            # Step title
            step_title = ttk.Label(step_frame, text=title, wraplength=80, justify=tk.CENTER)
            step_title.pack()
            
            # Duration
            duration_label = ttk.Label(step_frame, text=f"{duration} min", font=(self.design.fonts["primary"][0], 8))
            duration_label.pack()
            
            self.step_frames.append((indicator, step_title, duration_label))
        
        # Create content area - will hold different content based on current step
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Welcome content (initial view)
        self.welcome_frame = ttk.Frame(self.content_frame)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            self.welcome_frame,
            text="Ready for Your Optimized Study Session",
            style="Subheading.TLabel"
        ).pack(pady=20)
        
        desc_text = (
            "This 20-minute structured session is designed to maximize your learning efficiency "
            "and typing skills. Each phase focuses on different aspects of learning:\n\n"
            "1. Warm-Up - Light typing to get your fingers ready\n"
            "2. Targeted Drills - Focused practice on your weak areas\n"
            "3. Adaptive Challenge - Dynamic content based on your skill level\n"
            "4. Error-Focus Micro-Sessions - Intensive practice on problem areas\n"
            "5. Review & Spaced Repetition - Set up future learning\n"
            "6. Habit Tracking - Build consistency with reminders"
        )
        
        ttk.Label(
            self.welcome_frame,
            text=desc_text,
            wraplength=800,
            justify=tk.LEFT
        ).pack(pady=10)
        
        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = self.design.create_button(
            self.control_frame,
            "Start Session",
            command=self._start_session,
            style="primary"
        )
        self.start_button.pack(side=tk.RIGHT, padx=5)
        
        # Create frames for each step (initially hidden)
        self._create_step_frames()
    
    def _create_step_frames(self):
        """Create frames for each step of the session"""
        # 1. Warm-Up frame
        self.warmup_frame = ttk.Frame(self.content_frame)
        
        ttk.Label(
            self.warmup_frame,
            text="Warm-Up (2 minutes)",
            style="Subheading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.warmup_frame,
            text="Type these sentences to warm up your fingers. Real-time WPM and accuracy metrics will be displayed.",
            wraplength=800
        ).pack(pady=5)
        
        # Warmup text and input
        warmup_ref_frame, self.warmup_ref_text = self.design.create_text_input(
            self.warmup_frame, 
            height=3, 
            readonly=True
        )
        warmup_ref_frame.pack(fill=tk.X, pady=10)
        
        warmup_input_frame, self.warmup_input_text = self.design.create_text_input(
            self.warmup_frame, 
            height=3
        )
        warmup_input_frame.pack(fill=tk.X, pady=10)
        
        # Feedback canvas
        self.warmup_feedback = self.design.create_feedback_canvas(self.warmup_frame)
        self.warmup_feedback.pack(fill=tk.X, pady=5)
        
        # Bind key events
        self.warmup_input_text.bind("<KeyRelease>", self._update_warmup_feedback)
        
        # Performance metrics frame
        warmup_metrics = ttk.Frame(self.warmup_frame)
        warmup_metrics.pack(fill=tk.X, pady=10)
        
        # WPM and accuracy display
        metrics_left = ttk.Frame(warmup_metrics)
        metrics_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.warmup_wpm_var = tk.StringVar(value="WPM: 0")
        ttk.Label(metrics_left, textvariable=self.warmup_wpm_var, font=(self.design.fonts["secondary"][0], 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        self.warmup_accuracy_var = tk.StringVar(value="Accuracy: 0%")
        ttk.Label(metrics_left, textvariable=self.warmup_accuracy_var, font=(self.design.fonts["secondary"][0], 14)).pack(side=tk.LEFT, padx=20)
        
        # Next button
        self.warmup_next_btn = self.design.create_button(
            warmup_metrics,
            "Continue to Targeted Drills",
            command=lambda: self._go_to_step(1),
            style="primary"
        )
        self.warmup_next_btn.pack(side=tk.RIGHT, padx=5)
        self.warmup_next_btn.config(state=tk.DISABLED)
        
        # 2. Targeted Drills frame
        self.drills_frame = ttk.Frame(self.content_frame)
        
        ttk.Label(
            self.drills_frame,
            text="Targeted Drills (5 minutes)",
            style="Subheading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.drills_frame,
            text="Practice these frequently-missed letter combinations. Focus on accuracy over speed.",
            wraplength=800
        ).pack(pady=5)
        
        # Drill card
        self.drill_card = self.design.create_session_card(self.drills_frame, "Character Combination")
        self.drill_card.pack(fill=tk.X, pady=10)
        
        # Drill content
        self.drill_text_var = tk.StringVar(value="Loading drill...")
        ttk.Label(
            self.drill_card, 
            textvariable=self.drill_text_var, 
            font=(self.design.fonts["secondary"][0], 24),
            justify=tk.CENTER
        ).pack(pady=20)
        
        # Drill input
        drill_input_frame, self.drill_input_text = self.design.create_text_input(
            self.drill_card, 
            height=2
        )
        drill_input_frame.pack(fill=tk.X, pady=10)
        
        # Feedback canvas
        self.drill_feedback = self.design.create_feedback_canvas(self.drill_card)
        self.drill_feedback.pack(fill=tk.X, pady=5)
        
        # Bind key events
        self.drill_input_text.bind("<KeyRelease>", self._update_drill_feedback)
        
        # Drill controls
        drill_controls = ttk.Frame(self.drill_card)
        drill_controls.pack(fill=tk.X, pady=10)
        
        self.drill_submit_btn = self.design.create_button(
            drill_controls,
            "Submit",
            command=self._submit_drill,
            style="primary"
        )
        self.drill_submit_btn.pack(side=tk.LEFT, padx=5)
        
        self.drill_next_btn = self.design.create_button(
            drill_controls,
            "Next Drill",
            command=self._next_drill,
            style="secondary"
        )
        self.drill_next_btn.pack(side=tk.LEFT, padx=5)
        
        self.drill_continue_btn = self.design.create_button(
            drill_controls,
            "Continue to Adaptive Challenge",
            command=lambda: self._go_to_step(2),
            style="primary"
        )
        self.drill_continue_btn.pack(side=tk.RIGHT, padx=5)
        self.drill_continue_btn.config(state=tk.DISABLED)
        
        # 3. Adaptive Challenge frame
        self.adaptive_frame = ttk.Frame(self.content_frame)
        
        ttk.Label(
            self.adaptive_frame,
            text="Adaptive Challenge (5 minutes)",
            style="Subheading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.adaptive_frame,
            text="These challenges adapt to your skill level. Complete them in order for spaced repetition learning.",
            wraplength=800
        ).pack(pady=5)
        
        # Challenge card
        self.challenge_card = self.design.create_session_card(self.adaptive_frame, "Adaptive Challenge")
        self.challenge_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Challenge content
        challenge_content = ttk.Frame(self.challenge_card)
        challenge_content.pack(fill=tk.BOTH, expand=True)
        
        # Context
        self.challenge_context_var = tk.StringVar()
        ttk.Label(
            challenge_content, 
            textvariable=self.challenge_context_var,
            font=(self.design.fonts["primary"][0], 10, "italic")
        ).pack(anchor=tk.W, pady=5)
        
        # Prompt
        self.challenge_prompt_var = tk.StringVar()
        ttk.Label(
            challenge_content, 
            textvariable=self.challenge_prompt_var,
            font=(self.design.fonts["primary"][0], 14, "bold"),
            wraplength=800
        ).pack(pady=10)
        
        # Reference text
        reference_frame = ttk.LabelFrame(challenge_content, text="Reference Text (Type This)")
        reference_frame.pack(fill=tk.X, pady=10)
        
        reference_text_frame, self.challenge_reference = self.design.create_text_input(
            reference_frame, 
            height=3,
            readonly=True
        )
        reference_text_frame.pack(fill=tk.X, pady=10)
        
        # Input text
        input_frame = ttk.LabelFrame(challenge_content, text="Your Answer")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        input_text_frame, self.challenge_input = self.design.create_text_input(
            input_frame, 
            height=4
        )
        input_text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Feedback canvas
        self.challenge_feedback = self.design.create_feedback_canvas(input_frame)
        self.challenge_feedback.pack(fill=tk.X, pady=5)
        
        # Bind key events
        self.challenge_input.bind("<KeyRelease>", self._update_challenge_feedback)
        
        # Sparkline for speed trends
        sparkline_frame = ttk.Frame(challenge_content)
        sparkline_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sparkline_frame, text="Speed Trend:").pack(side=tk.LEFT)
        self.challenge_sparkline = self.design.create_sparkline(sparkline_frame)
        self.challenge_sparkline.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Challenge controls
        challenge_controls = ttk.Frame(self.challenge_card)
        challenge_controls.pack(fill=tk.X, pady=10)
        
        self.challenge_submit_btn = self.design.create_button(
            challenge_controls,
            "Submit",
            command=self._submit_challenge,
            style="primary"
        )
        self.challenge_submit_btn.pack(side=tk.LEFT, padx=5)
        
        self.challenge_next_btn = self.design.create_button(
            challenge_controls,
            "Next Challenge",
            command=self._next_challenge,
            style="secondary"
        )
        self.challenge_next_btn.pack(side=tk.LEFT, padx=5)
        self.challenge_next_btn.config(state=tk.DISABLED)
        
        self.challenge_continue_btn = self.design.create_button(
            challenge_controls,
            "Continue to Error Focus",
            command=lambda: self._go_to_step(3),
            style="primary"
        )
        self.challenge_continue_btn.pack(side=tk.RIGHT, padx=5)
        self.challenge_continue_btn.config(state=tk.DISABLED)
        
        # 4. Error Focus frame
        self.errorfocus_frame = ttk.Frame(self.content_frame)
        
        ttk.Label(
            self.errorfocus_frame,
            text="Error-Focus Micro-Sessions (3 minutes)",
            style="Subheading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.errorfocus_frame,
            text="Focus on your top error-prone items. Complete each item correctly twice to master it.",
            wraplength=800
        ).pack(pady=5)
        
        # Error card
        self.error_card = self.design.create_session_card(self.errorfocus_frame, "Error Focus")
        self.error_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Card header with difficulty indicator
        error_header = ttk.Frame(self.error_card)
        error_header.pack(fill=tk.X)
        
        self.error_title_var = tk.StringVar(value="Error Item")
        ttk.Label(error_header, textvariable=self.error_title_var, font=(self.design.fonts["primary"][0], 14, "bold")).pack(side=tk.LEFT)
        
        self.error_difficulty_var = tk.StringVar()
        self.error_difficulty_label = ttk.Label(error_header, textvariable=self.error_difficulty_var)
        self.error_difficulty_label.pack(side=tk.RIGHT)
        
        # Error content
        error_content = ttk.Frame(self.error_card)
        error_content.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Reference text
        error_ref_frame, self.error_reference = self.design.create_text_input(
            error_content, 
            height=3,
            readonly=True
        )
        error_ref_frame.pack(fill=tk.X, pady=10)
        
        # Input text
        error_input_frame, self.error_input = self.design.create_text_input(
            error_content, 
            height=3
        )
        error_input_frame.pack(fill=tk.X, pady=10)
        
        # Feedback canvas
        self.error_feedback = self.design.create_feedback_canvas(error_content)
        self.error_feedback.pack(fill=tk.X, pady=5)
        
        # Bind key events
        self.error_input.bind("<KeyRelease>", self._update_error_feedback)
        
        # Progress indicator
        self.error_progress_var = tk.StringVar(value="Correct: 0/2")
        ttk.Label(error_content, textvariable=self.error_progress_var).pack(anchor=tk.E, pady=5)
        
        # Error controls
        error_controls = ttk.Frame(self.error_card)
        error_controls.pack(fill=tk.X, pady=10)
        
        self.error_submit_btn = self.design.create_button(
            error_controls,
            "Submit",
            command=self._submit_error,
            style="primary"
        )
        self.error_submit_btn.pack(side=tk.LEFT, padx=5)
        
        self.error_next_btn = self.design.create_button(
            error_controls,
            "Next Error Item",
            command=self._next_error,
            style="secondary"
        )
        self.error_next_btn.pack(side=tk.LEFT, padx=5)
        self.error_next_btn.config(state=tk.DISABLED)
        
        self.error_continue_btn = self.design.create_button(
            error_controls,
            "Continue to Review",
            command=lambda: self._go_to_step(4),
            style="primary"
        )
        self.error_continue_btn.pack(side=tk.RIGHT, padx=5)
        self.error_continue_btn.config(state=tk.DISABLED)
        
        # 5. Review frame
        self.review_frame = ttk.Frame(self.content_frame)
        
        ttk.Label(
            self.review_frame,
            text="Review & Spaced Repetition Setup (3 minutes)",
            style="Subheading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.review_frame,
            text="Review your progress and set up your next spaced repetition session.",
            wraplength=800
        ).pack(pady=5)
        
        # Summary card
        summary_card = self.design.create_session_card(self.review_frame, "Session Summary")
        summary_card.pack(fill=tk.X, pady=10)
        
        # Stats
        stats_frame = ttk.Frame(summary_card)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.review_items_var = tk.StringVar(value="Items completed: 0")
        self.review_accuracy_var = tk.StringVar(value="Average accuracy: 0%")
        self.review_wpm_var = tk.StringVar(value="Average WPM: 0")
        
        ttk.Label(stats_frame, textvariable=self.review_items_var, font=(self.design.fonts["primary"][0], 12)).pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, textvariable=self.review_accuracy_var, font=(self.design.fonts["primary"][0], 12)).pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, textvariable=self.review_wpm_var, font=(self.design.fonts["primary"][0], 12)).pack(anchor=tk.W, pady=2)
        
        # Spaced repetition queue
        queue_frame = ttk.LabelFrame(self.review_frame, text="Next Review Queue")
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Item list with importance slider
        self.queue_listbox = tk.Listbox(
            queue_frame,
            height=8,
            font=(self.design.fonts["primary"][0], 12)
        )
        self.queue_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Importance adjustment
        importance_frame = ttk.Frame(queue_frame)
        importance_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(importance_frame, text="Importance:").pack(side=tk.LEFT)
        
        self.importance_var = tk.IntVar(value=5)
        importance_scale = ttk.Scale(
            importance_frame, 
            from_=1, 
            to=10, 
            variable=self.importance_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        importance_scale.pack(side=tk.LEFT, padx=10)
        
        self.importance_label = ttk.Label(importance_frame, text="5")
        self.importance_label.pack(side=tk.LEFT)
        
        # Update importance label when scale changes
        importance_scale.bind("<Motion>", lambda e: self.importance_label.config(
            text=str(self.importance_var.get())
        ))
        
        # Apply button
        self.importance_apply_btn = self.design.create_button(
            importance_frame,
            "Apply",
            command=self._apply_importance,
            style="secondary"
        )
        self.importance_apply_btn.pack(side=tk.LEFT, padx=10)
        
        # Review controls
        review_controls = ttk.Frame(self.review_frame)
        review_controls.pack(fill=tk.X, pady=10)
        
        self.review_continue_btn = self.design.create_button(
            review_controls,
            "Continue to Habit Tracking",
            command=lambda: self._go_to_step(5),
            style="primary"
        )
        self.review_continue_btn.pack(side=tk.RIGHT, padx=5)
        
        # 6. Habit Tracking frame
        self.habit_frame = ttk.Frame(self.content_frame)
        
        ttk.Label(
            self.habit_frame,
            text="Habit Cadence & Reminder (2 minutes)",
            style="Subheading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.habit_frame,
            text="Schedule your next study session and set up reminders to build a consistent study habit.",
            wraplength=800
        ).pack(pady=5)
        
        # Calendar card
        calendar_card = self.design.create_session_card(self.habit_frame, "Study Cadence")
        calendar_card.pack(fill=tk.X, pady=10)
        
        # Current streak
        streak_frame = ttk.Frame(calendar_card)
        streak_frame.pack(fill=tk.X, pady=10)
        
        self.streak_var = tk.StringVar(value="Current streak: 1 day")
        ttk.Label(streak_frame, textvariable=self.streak_var, font=(self.design.fonts["primary"][0], 14, "bold")).pack(side=tk.LEFT)
        
        # Mini calendar showing last 7 days
        calendar_view = ttk.Frame(calendar_card)
        calendar_view.pack(fill=tk.X, pady=10)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.day_frames = []
        
        for i, day in enumerate(days):
            day_frame = ttk.Frame(calendar_view)
            day_frame.grid(row=0, column=i, padx=5)
            
            ttk.Label(day_frame, text=day).pack()
            
            day_indicator = tk.Canvas(day_frame, width=30, height=30, highlightthickness=0)
            day_indicator.create_oval(5, 5, 25, 25, outline=self.design.colors["primary"], width=1)
            day_indicator.pack(pady=5)
            
            self.day_frames.append(day_indicator)
        
        # Next session scheduling
        next_session_frame = ttk.LabelFrame(self.habit_frame, text="Schedule Next Session")
        next_session_frame.pack(fill=tk.X, pady=10)
        
        schedule_frame = ttk.Frame(next_session_frame)
        schedule_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(schedule_frame, text="Next study session:").pack(side=tk.LEFT)
        
        # Default to tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        default_time = tomorrow.strftime("%Y-%m-%d 10:00")
        
        self.schedule_var = tk.StringVar(value=default_time)
        schedule_entry = ttk.Entry(schedule_frame, textvariable=self.schedule_var, width=20)
        schedule_entry.pack(side=tk.LEFT, padx=10)
        
        # Remind me checkbox
        self.remind_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(schedule_frame, text="Set reminder", variable=self.remind_var).pack(side=tk.LEFT, padx=20)
        
        # Set button
        self.schedule_btn = self.design.create_button(
            schedule_frame,
            "Schedule Session",
            command=self._schedule_session,
            style="primary"
        )
        self.schedule_btn.pack(side=tk.RIGHT, padx=5)
        
        # Complete button
        complete_frame = ttk.Frame(self.habit_frame)
        complete_frame.pack(fill=tk.X, pady=20)
        
        self.complete_btn = self.design.create_button(
            complete_frame,
            "Complete Session",
            command=self._complete_session,
            style="primary"
        )
        self.complete_btn.pack(pady=10)
        
        # Hide all step frames initially
        self._hide_step_frames()
    
    def _hide_step_frames(self):
        """Hide all step frames"""
        self.warmup_frame.pack_forget()
        self.drills_frame.pack_forget()
        self.adaptive_frame.pack_forget()
        self.errorfocus_frame.pack_forget()
        self.review_frame.pack_forget()
        self.habit_frame.pack_forget()
    
    def _highlight_current_step(self, step):
        """Highlight the current step in the flow visualization"""
        # Reset all indicators
        for i, (indicator, title, duration) in enumerate(self.step_frames):
            if i == step:
                # Highlight current step
                indicator.delete("all")
                indicator.create_oval(5, 5, 35, 35, fill=self.design.colors["primary"], outline="")
                indicator.create_text(20, 20, text=str(i+1), fill="#FFFFFF")
                title.configure(font=(self.design.fonts["primary"][0], 10, "bold"))
            elif i < step:
                # Mark completed steps
                indicator.delete("all")
                indicator.create_oval(5, 5, 35, 35, fill=self.design.colors["secondary"], outline="")
                indicator.create_text(20, 20, text="✓", fill="#FFFFFF")
                title.configure(font=(self.design.fonts["primary"][0], 10))
            else:
                # Reset future steps
                indicator.delete("all")
                indicator.create_oval(5, 5, 35, 35, outline=self.design.colors["primary"], width=2, fill="")
                indicator.create_text(20, 20, text=str(i+1), fill=self.design.colors["primary"])
                title.configure(font=(self.design.fonts["primary"][0], 10))
    
    def _start_session(self):
        """Start the study session"""
        if not self.study_items:
            messagebox.showinfo("No Study Items", "Please load or create study items first.")
            return
        
        # Initialize session
        self.session_active = True
        self.current_step = 0
        self.session_start_time = datetime.now()
        self.step_start_time = datetime.now()
        
        # Clear history
        self.wpm_history = []
        self.accuracy_history = []
        self.error_items = []
        
        # Update UI
        self.welcome_frame.pack_forget()
        self._go_to_step(0)  # Start with warm-up
        
        # Start timer
        self._start_timer()
        
        # Disable start button
        self.start_button.config(state=tk.DISABLED)
    
    def _start_timer(self):
        """Start session timer"""
        self.timer_running = True
        
        def update_timer():
            while self.timer_running:
                if self.session_start_time:
                    elapsed = (datetime.now() - self.session_start_time).total_seconds()
                    minutes, seconds = divmod(int(elapsed), 60)
                    
                    # Update timer display
                    self.timer_var.set(f"Time: {minutes}:{seconds:02d}")
                    
                    # Check for step time limit (for auto-advancement)
                    if self.step_start_time:
                        step_elapsed = (datetime.now() - self.step_start_time).total_seconds()
                        step_limit = self.step_durations[self.current_step] * 60  # convert to seconds
                        
                        # Update progress bar
                        progress_value = min(100, (step_elapsed / step_limit) * 100)
                        self.progress.config(value=progress_value)
                        
                        # Auto-advance after time limit (add 5 seconds grace period)
                        if step_elapsed > (step_limit + 5) and self.current_step < 5:
                            # Run in main thread
                            self.parent.after(0, lambda: self._go_to_step(self.current_step + 1))
                
                time.sleep(1)
        
        # Start timer thread
        threading.Thread(target=update_timer, daemon=True).start()
    
    def _go_to_step(self, step):
        """Go to a specific step in the session flow"""
        # Validate step
        if step < 0 or step > 5:
            return
        
        # Update current step
        self.current_step = step
        self.step_start_time = datetime.now()
        
        # Hide all step frames
        self._hide_step_frames()
        
        # Update step highlight
        self._highlight_current_step(step)
        
        # Reset progress bar
        self.progress.config(value=0)
        
        # Show appropriate frame based on step
        step_titles = [
            "Warm-Up (2 minutes)", 
            "Targeted Drills (5 minutes)", 
            "Adaptive Challenge (5 minutes)",
            "Error-Focus Micro-Sessions (3 minutes)",
            "Review & Spaced Repetition (3 minutes)",
            "Habit Tracking (2 minutes)"
        ]
        
        step_descriptions = [
            "Type these sentences to warm up your fingers and get ready for the session.",
            "Focus on these high-frequency weak letter combinations to improve accuracy.",
            "These adaptive challenges will test your mastery through spaced repetition.",
            "Practice items with the most errors until you can type them correctly.",
            "Review your progress and set up your next spaced repetition session.",
            "Track your study streak and schedule your next session."
        ]
        
        self.step_label.config(text=step_titles[step])
        self.progress_desc.config(text=step_descriptions[step])
        
        # Initialize step-specific content
        if step == 0:  # Warm-Up
            self.warmup_frame.pack(fill=tk.BOTH, expand=True)
            self._init_warmup()
        elif step == 1:  # Targeted Drills
            self.drills_frame.pack(fill=tk.BOTH, expand=True)
            self._init_drills()
        elif step == 2:  # Adaptive Challenge
            self.adaptive_frame.pack(fill=tk.BOTH, expand=True)
            self._init_adaptive()
        elif step == 3:  # Error Focus
            self.errorfocus_frame.pack(fill=tk.BOTH, expand=True)
            self._init_error_focus()
        elif step == 4:  # Review
            self.review_frame.pack(fill=tk.BOTH, expand=True)
            self._init_review()
        elif step == 5:  # Habit Tracking
            self.habit_frame.pack(fill=tk.BOTH, expand=True)
            self._init_habit_tracking()
    
    def _init_warmup(self):
        """Initialize the warm-up step"""
        # Set a simple warm-up text
        warmup_texts = [
            "The quick brown fox jumps over the lazy dog. This pangram contains all the letters of the alphabet.",
            "How vexingly quick daft zebras jump! Five or six big jet planes zoomed quickly by the new tower.",
            "Pack my box with five dozen liquor jugs. We promptly judged antique ivory buckles for the next prize.",
            "As you practice typing, focus on accuracy first, then speed will naturally follow with consistent practice.",
            "Developing good typing habits early will save you time and reduce strain over your lifetime of keyboard use."
        ]
        
        self.warmup_text = random.choice(warmup_texts)
        self.warmup_ref_text.config(state=tk.NORMAL)
        self.warmup_ref_text.delete("1.0", tk.END)
        self.warmup_ref_text.insert("1.0", self.warmup_text)
        self.warmup_ref_text.config(state=tk.DISABLED)
        
        # Clear input
        self.warmup_input_text.delete("1.0", tk.END)
        
        # Clear feedback
        self.warmup_feedback.delete("all")
        
        # Reset metrics
        self.warmup_wpm_var.set("WPM: 0")
        self.warmup_accuracy_var.set("Accuracy: 0%")
        
        # Start typing timer
        self.warmup_start_time = datetime.now()
        
        # Enable next button after delay
        self.parent.after(10000, lambda: self.warmup_next_btn.config(state=tk.NORMAL))
    
    def _update_warmup_feedback(self, event):
        """Update warm-up feedback on typing"""
        typed = self.warmup_input_text.get("1.0", tk.END).strip()
        expected = self.warmup_text
        
        # Update feedback visualization
        self.design.update_feedback_canvas(self.warmup_feedback, typed, expected)
        
        # Calculate WPM and accuracy
        if typed:
            # Time elapsed in minutes
            time_elapsed = (datetime.now() - self.warmup_start_time).total_seconds() / 60
            if time_elapsed > 0:
                # Words = characters / 5
                words = len(typed) / 5
                wpm = words / time_elapsed
                
                # Calculate accuracy
                matches = sum(1 for a, b in zip(typed, expected) if a == b)
                accuracy = matches / min(len(typed), len(expected)) if len(typed) > 0 else 0
                
                # Update display
                self.warmup_wpm_var.set(f"WPM: {wpm:.1f}")
                self.warmup_accuracy_var.set(f"Accuracy: {accuracy*100:.1f}%")
                
                # Save metrics for history
                if len(typed) > 5:  # Only record if meaningful amount typed
                    self.wpm_history.append(wpm)
                    self.accuracy_history.append(accuracy)
    
    def _init_drills(self):
        """Initialize the targeted drills step"""
        # Common difficult character combinations
        self.drill_combinations = [
            "th", "er", "on", "an", "re", 
            "he", "in", "ed", "nd", "ha",
            "at", "en", "es", "of", "or",
            "nt", "ea", "ti", "to", "io",
            "le", "is", "ou", "ar", "as"
        ]
        
        # Start with first drill
        self.current_drill_index = 0
        self.drill_completed = set()
        self._load_drill()
        
        # Enable/disable buttons
        self.drill_submit_btn.config(state=tk.NORMAL)
        self.drill_next_btn.config(state=tk.NORMAL)
        self.drill_continue_btn.config(state=tk.DISABLED)
    
    def _load_drill(self):
        """Load the next drill"""
        if self.current_drill_index >= len(self.drill_combinations):
            self.current_drill_index = 0
        
        # Get current combination
        combo = self.drill_combinations[self.current_drill_index]
        
        # Create a practice string with this combination
        words = []
        for _ in range(5):
            prefix = ''.join(random.choice('bcdfghjklmnpqrstvwxyz') for _ in range(random.randint(1, 2)))
            suffix = ''.join(random.choice('bcdfghjklmnpqrstvwxyz') for _ in range(random.randint(1, 2)))
            vowel = random.choice('aeiou')
            
            # Create word with the target combination
            if random.random() < 0.5:
                word = prefix + combo + suffix
            else:
                word = prefix + vowel + combo + suffix
            
            words.append(word)
        
        # Create drill text
        self.current_drill = ' '.join(words)
        self.drill_text_var.set(f"Type: {self.current_drill}")
        
        # Clear input
        self.drill_input_text.delete("1.0", tk.END)
        
        # Clear feedback
        self.drill_feedback.delete("all")
    
    def _update_drill_feedback(self, event):
        """Update drill feedback on typing"""
        typed = self.drill_input_text.get("1.0", tk.END).strip()
        expected = self.current_drill
        
        # Update feedback visualization
        self.design.update_feedback_canvas(self.drill_feedback, typed, expected)
    
    def _submit_drill(self):
        """Submit the current drill"""
        typed = self.drill_input_text.get("1.0", tk.END).strip()
        expected = self.current_drill
        
        # Calculate accuracy
        matches = sum(1 for a, b in zip(typed, expected) if a == b)
        accuracy = matches / len(expected) if expected else 0
        
        # Mark as completed
        self.drill_completed.add(self.current_drill_index)
        
        # Add to error items if accuracy is low
        if accuracy < 0.9:
            combo = self.drill_combinations[self.current_drill_index]
            error_item = StudyItem(
                prompt=f"Practice the combination: {combo}",
                answer=self.current_drill,
                context="Character Drills",
                item_type=StudyItemType.KEY_CONCEPT,
                importance=8
            )
            self.error_items.append(error_item)
        
        # Show feedback
        if accuracy > 0.95:
            self.design.create_toast_notification("Excellent! Perfect drill completion!")
        elif accuracy > 0.8:
            self.design.create_toast_notification("Good job! Keep practicing for perfection.")
        else:
            self.design.create_toast_notification("This combination needs more practice.")
        
        # Enable continue button if enough drills completed
        if len(self.drill_completed) >= 5:
            self.drill_continue_btn.config(state=tk.NORMAL)
    
    def _next_drill(self):
        """Move to the next drill"""
        self.current_drill_index += 1
        self._load_drill()
    
    def _init_adaptive(self):
        """Initialize the adaptive challenge step"""
        # Reset counters
        self.challenge_count = 0
        self.challenge_completed = 0
        
        # Clear sparkline data
        self.challenge_speeds = []
        
        # Start with first challenge
        self._load_next_challenge()
        
        # Enable/disable buttons
        self.challenge_submit_btn.config(state=tk.NORMAL)
        self.challenge_next_btn.config(state=tk.DISABLED)
        self.challenge_continue_btn.config(state=tk.DISABLED)
    
    def _load_next_challenge(self):
        """Load the next adaptive challenge"""
        # Get next item from learning tracker
        study_item = self.learning_tracker.get_next_item()
        
        if not study_item:
            # If no items from tracker, use a random one
            if self.study_items:
                study_item = random.choice(self.study_items)
            else:
                # Create a placeholder item if no items available
                study_item = StudyItem(
                    prompt="Sample challenge prompt",
                    answer="This is a sample challenge answer for typing practice.",
                    context="Sample",
                    item_type=StudyItemType.KEY_CONCEPT,
                    importance=5
                )
        
        # Create a challenge
        self.current_challenge = TypingChallenge(study_item)
        self.current_challenge.start()
        
        # Update UI
        self.challenge_context_var.set(f"Context: {study_item.context} • Type: {study_item.item_type.value}")
        self.challenge_prompt_var.set(study_item.prompt)
        
        # Set reference text
        self.challenge_reference.config(state=tk.NORMAL)
        self.challenge_reference.delete("1.0", tk.END)
        self.challenge_reference.insert(tk.END, study_item.answer)
        self.challenge_reference.config(state=tk.DISABLED)
        
        # Clear input
        self.challenge_input.delete("1.0", tk.END)
        
        # Clear feedback
        self.challenge_feedback.delete("all")
        
        # Increment counter
        self.challenge_count += 1
    
    def _update_challenge_feedback(self, event):
        """Update challenge feedback on typing"""
        if not self.current_challenge:
            return
        
        typed = self.challenge_input.get("1.0", tk.END).strip()
        expected = self.current_challenge.study_item.answer
        
        # Update feedback visualization
        self.design.update_feedback_canvas(self.challenge_feedback, typed, expected)
    
    def _submit_challenge(self):
        """Submit the current challenge"""
        if not self.current_challenge:
            return
        
        # Get typed text
        typed = self.challenge_input.get("1.0", tk.END).strip()
        
        # Complete the challenge
        results = self.current_challenge.complete(typed)
        
        # Record results
        self.learning_tracker.record_challenge_result(results)
        
        # Save speed for sparkline
        self.challenge_speeds.append(results.get("wpm", 0))
        
        # Update sparkline
        self.design.update_sparkline(self.challenge_sparkline, self.challenge_speeds)
        
        # Check accuracy for error items
        accuracy = results.get("accuracy", 0)
        if accuracy < 0.9:
            # Add to error items
            self.error_items.append(self.current_challenge.study_item)
        
        # Show feedback
        if accuracy > 0.95:
            self.design.create_toast_notification("Excellent challenge completion!")
        elif accuracy > 0.8:
            self.design.create_toast_notification("Good job on this challenge!")
        else:
            self.design.create_toast_notification("This item will need more practice.")
        
        # Update UI
        self.challenge_submit_btn.config(state=tk.DISABLED)
        self.challenge_next_btn.config(state=tk.NORMAL)
        
        # Increment completed counter
        self.challenge_completed += 1
        
        # Enable continue button after enough challenges
        if self.challenge_completed >= 5:
            self.challenge_continue_btn.config(state=tk.NORMAL)
    
    def _next_challenge(self):
        """Move to the next challenge"""
        self._load_next_challenge()
        
        # Reset button states
        self.challenge_submit_btn.config(state=tk.NORMAL)
        self.challenge_next_btn.config(state=tk.DISABLED)
    
    def _init_error_focus(self):
        """Initialize the error focus step"""
        # Prepare error items
        if not self.error_items:
            # If no error items collected, use items with low mastery
            for item in self.study_items:
                if item.mastery < 0.5:
                    self.error_items.append(item)
            
            # If still no items, use random items
            if not self.error_items and self.study_items:
                self.error_items = random.sample(self.study_items, 
                                                min(3, len(self.study_items)))
        
        # Sort by importance and take top 3
        self.error_items.sort(key=lambda x: x.importance, reverse=True)
        self.error_items = self.error_items[:3]
        
        # Set up error tracking
        self.current_error_index = 0
        self.error_correct_count = {}  # Track correct answers for each item
        
        # Load first error item
        self._load_error_item()
    
    def _load_error_item(self):
        """Load the next error item"""
        if not self.error_items or self.current_error_index >= len(self.error_items):
            # No more error items or completed all
            self.error_continue_btn.config(state=tk.NORMAL)
            return
        
        # Get current error item
        error_item = self.error_items[self.current_error_index]
        
        # Set difficulty indicator
        if error_item.mastery < 0.3:
            self.error_difficulty_var.set("🔴 High Difficulty")
            self.error_difficulty_label.config(foreground="#F44336")
        elif error_item.mastery < 0.7:
            self.error_difficulty_var.set("🟡 Medium Difficulty")
            self.error_difficulty_label.config(foreground="#FFC107")
        else:
            self.error_difficulty_var.set("🟢 Low Difficulty")
            self.error_difficulty_label.config(foreground="#4CAF50")
        
        # Set title
        self.error_title_var.set(f"Error Item {self.current_error_index + 1} of {len(self.error_items)}")
        
        # Set reference text
        self.error_reference.config(state=tk.NORMAL)
        self.error_reference.delete("1.0", tk.END)
        self.error_reference.insert(tk.END, error_item.answer)
        self.error_reference.config(state=tk.DISABLED)
        
        # Clear input
        self.error_input.delete("1.0", tk.END)
        
        # Clear feedback
        self.error_feedback.delete("all")
        
        # Get current correct count
        correct_count = self.error_correct_count.get(error_item.id, 0)
        self.error_progress_var.set(f"Correct: {correct_count}/2")
        
        # Reset button states
        self.error_submit_btn.config(state=tk.NORMAL)
        self.error_next_btn.config(state=tk.DISABLED)
    
    def _update_error_feedback(self, event):
        """Update error focus feedback on typing"""
        if not self.error_items or self.current_error_index >= len(self.error_items):
            return
        
        typed = self.error_input.get("1.0", tk.END).strip()
        expected = self.error_items[self.current_error_index].answer
        
        # Update feedback visualization
        self.design.update_feedback_canvas(self.error_feedback, typed, expected)
    
    def _submit_error(self):
        """Submit the current error item"""
        if not self.error_items or self.current_error_index >= len(self.error_items):
            return
        
        typed = self.error_input.get("1.0", tk.END).strip()
        error_item = self.error_items[self.current_error_index]
        expected = error_item.answer
        
        # Calculate accuracy
        matches = sum(1 for a, b in zip(typed, expected) if a == b)
        accuracy = matches / len(expected) if expected else 0
        
        # Check if correct (over 95% accuracy)
        if accuracy > 0.95:
            # Increment correct count
            current_correct = self.error_correct_count.get(error_item.id, 0)
            current_correct += 1
            self.error_correct_count[error_item.id] = current_correct
            
            # Update progress display
            self.error_progress_var.set(f"Correct: {current_correct}/2")
            
            # Show success message
            self.design.create_toast_notification("Correct! Well done!")
            
            # Enable next button
            self.error_next_btn.config(state=tk.NORMAL)
            
            # If reached 2 correct, automatically move to next
            if current_correct >= 2:
                self.parent.after(1000, self._next_error)
        else:
            # Show try again message
            self.design.create_toast_notification("Not quite right. Try again!")
            
            # Clear input for retry
            self.error_input.delete("1.0", tk.END)
    
    def _next_error(self):
        """Move to the next error item"""
        self.current_error_index += 1
        
        # If we've reached the end of the items
        if self.current_error_index >= len(self.error_items):
            # Enable continue button
            self.error_continue_btn.config(state=tk.NORMAL)
            
            # Show completion message
            self.design.create_toast_notification("Error focus completed!")
        else:
            # Load next error item
            self._load_error_item()
    
    def _init_review(self):
        """Initialize the review and spaced repetition step"""
        # Calculate session statistics
        total_items = self.challenge_completed + len(self.drill_completed)
        
        # Average WPM
        avg_wpm = 0
        if self.wpm_history:
            avg_wpm = sum(self.wpm_history) / len(self.wpm_history)
        
        # Average accuracy
        avg_accuracy = 0
        if self.accuracy_history:
            avg_accuracy = sum(self.accuracy_history) / len(self.accuracy_history)
        
        # Update display
        self.review_items_var.set(f"Items completed: {total_items}")
        self.review_accuracy_var.set(f"Average accuracy: {avg_accuracy*100:.1f}%")
        self.review_wpm_var.set(f"Average WPM: {avg_wpm:.1f}")
        
        # Fill queue listbox
        self.queue_listbox.delete(0, tk.END)
        
        # Get due items
        due_items = self.learning_tracker.spaced_repetition.get_due_items()
        
        # If no due items, use random selection
        if not due_items and self.study_items:
            due_items = random.sample(self.study_items, min(10, len(self.study_items)))
        
        # Add to listbox
        for i, item in enumerate(due_items):
            # Format text with importance
            label = f"{i+1}. {item.prompt[:40]}... [Importance: {item.importance}]"
            self.queue_listbox.insert(tk.END, label)
        
        # Enable continue button
        self.review_continue_btn.config(state=tk.NORMAL)
    
    def _apply_importance(self):
        """Apply importance setting to selected item"""
        selected = self.queue_listbox.curselection()
        if not selected:
            return
        
        # Get selected index
        idx = selected[0]
        
        # Get due items
        due_items = self.learning_tracker.spaced_repetition.get_due_items()
        
        # If no due items, use random selection
        if not due_items and self.study_items:
            due_items = random.sample(self.study_items, min(10, len(self.study_items)))
        
        if idx < len(due_items):
            # Get the selected item
            item = due_items[idx]
            
            # Update importance
            item.importance = self.importance_var.get()
            
            # Update display
            self.queue_listbox.delete(idx)
            label = f"{idx+1}. {item.prompt[:40]}... [Importance: {item.importance}]"
            self.queue_listbox.insert(idx, label)
            
            # Show confirmation
            self.design.create_toast_notification(f"Importance updated to {item.importance}")
    
    def _init_habit_tracking(self):
        """Initialize the habit tracking step"""
        # Update streak display (mock data for demo)
        streak_days = 1
        if hasattr(self.master_app, 'streak_days'):
            streak_days = self.master_app.streak_days
        
        self.streak_var.set(f"Current streak: {streak_days} day{'s' if streak_days != 1 else ''}")
        
        # Update calendar visualization (mock data for demo)
        practice_days = []
        today = datetime.now().weekday()
        
        # Simple pattern - practiced yesterday and today
        if today > 0:
            practice_days.append(today - 1)  # Yesterday
        practice_days.append(today)  # Today
        
        # Visualize in calendar
        for i, day_canvas in enumerate(self.day_frames):
            day_canvas.delete("all")
            
            if i in practice_days:
                # Practiced day
                day_canvas.create_oval(5, 5, 25, 25, fill=self.design.colors["primary"], outline="")
                day_canvas.create_text(15, 15, text="✓", fill="#FFFFFF")
            else:
                # Regular day
                day_canvas.create_oval(5, 5, 25, 25, outline=self.design.colors["primary"], width=1)
        
        # Set default date for next session
        tomorrow = datetime.now() + timedelta(days=1)
        default_time = tomorrow.strftime("%Y-%m-%d 10:00")
        self.schedule_var.set(default_time)
    
    def _schedule_session(self):
        """Schedule the next session"""
        scheduled_time = self.schedule_var.get()
        
        # Validate format
        try:
            datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
            valid = True
        except ValueError:
            valid = False
        
        if not valid:
            messagebox.showwarning("Invalid Date", "Please enter date in format: YYYY-MM-DD HH:MM")
            return
        
        # Set reminder if requested
        if self.remind_var.get():
            # In a real app, this would set up an actual reminder
            # For demo, just show a confirmation
            self.design.create_toast_notification(f"Reminder set for {scheduled_time}")
        
        # Show confirmation
        self.design.create_toast_notification("Next session scheduled!")
        
        # Update button state
        self.schedule_btn.config(state=tk.DISABLED)
    
    def _complete_session(self):
        """Complete the study session"""
        # Stop timer
        self.timer_running = False
        
        # Save progress to learning tracker
        self.learning_tracker.save_progress()
        
        # Calculate session duration
        duration = 0
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).total_seconds() / 60.0
        
        # Show summary
        summary = f"Session completed!\n\n" \
                  f"Duration: {duration:.1f} minutes\n" \
                  f"Items practiced: {self.challenge_completed + len(self.drill_completed)}\n"
        
        if self.wpm_history:
            avg_wpm = sum(self.wpm_history) / len(self.wpm_history)
            summary += f"Average speed: {avg_wpm:.1f} WPM\n"
            
        if self.accuracy_history:
            avg_acc = sum(self.accuracy_history) / len(self.accuracy_history)
            summary += f"Average accuracy: {avg_acc*100:.1f}%\n"
        
        messagebox.showinfo("Session Complete", summary)
        
        # Increment streak
        if hasattr(self.master_app, 'streak_days'):
            self.master_app.streak_days += 1
        
        # Reset UI for a new session
        self._hide_step_frames()
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        # Enable start button
        self.start_button.config(state=tk.NORMAL)
        
        # Reset session state
        self.session_active = False
        self.current_step = 0
        
        # Add to session history if possible
        if hasattr(self.master_app, 'sessions_table'):
            # Format data for table
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            duration_str = f"{duration:.1f} min"
            items_count = self.challenge_completed + len(self.drill_completed)
            
            avg_acc_str = "N/A"
            if self.accuracy_history:
                avg_acc = sum(self.accuracy_history) / len(self.accuracy_history)
                avg_acc_str = f"{avg_acc*100:.1f}%"
            
            avg_wpm_str = "N/A"
            if self.wpm_history:
                avg_wpm = sum(self.wpm_history) / len(self.wpm_history)
                avg_wpm_str = f"{avg_wpm:.1f}"
            
            # Insert into table
            self.master_app.sessions_table.insert("", 0, values=(
                now, duration_str, items_count, avg_acc_str, avg_wpm_str
            ))


if __name__ == "__main__":
    # Test the session manager
    root = tk.Tk()
    root.title("Study Session Manager")
    root.geometry("900x700")
    
    # Create a mock master app
    class MockApp:
        def __init__(self):
            self.study_items = []
            self.learning_tracker = LearningTracker()
            self.streak_days = 1
    
    # Create some sample study items
    sample_items = []
    for i in range(10):
        item = StudyItem(
            prompt=f"Sample study item {i+1}",
            answer=f"This is the answer for study item {i+1} that you need to type.",
            context="Sample",
            item_type=StudyItemType.KEY_CONCEPT,
            importance=random.randint(3, 8)
        )
        sample_items.append(item)
    
    # Create mock app
    mock_app = MockApp()
    mock_app.study_items = sample_items
    mock_app.learning_tracker.load_study_items(sample_items)
    
    # Import design system
    from design_system import TypingStudyDesignSystem
    design = TypingStudyDesignSystem(root)
    
    # Create session manager
    manager = StudySessionManager(root, mock_app, design)
    
    root.mainloop()