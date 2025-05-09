# integration/sequential_practice.py

import os
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Iterator, Tuple

from parser.study_item import StudyItem, StudyItemType
from integration.challenge_generator import TypingChallenge


class SequentialPractice:
    """Provides sequential practice through study items from start to finish"""
    
    def __init__(self, study_items: List[StudyItem] = None):
        self.study_items = study_items or []
        self.current_index = 0
        self.session_results: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def add_items(self, items: List[StudyItem]) -> None:
        """Add study items to the practice session"""
        self.study_items.extend(items)
    
    def start_session(self) -> None:
        """Start a new practice session"""
        self.current_index = 0
        self.session_results = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def end_session(self) -> Dict[str, Any]:
        """End the current practice session and get summary statistics"""
        self.end_time = datetime.now()
        
        # Calculate session duration
        if self.start_time:
            duration_minutes = (self.end_time - self.start_time).total_seconds() / 60.0
        else:
            duration_minutes = 0
        
        # Calculate session statistics
        total_items = len(self.session_results)
        if total_items == 0:
            return {
                "duration_minutes": duration_minutes,
                "items_completed": 0,
                "average_accuracy": 0,
                "average_wpm": 0,
                "completion_percentage": 0,
                "date": self.end_time.strftime("%Y-%m-%d %H:%M")
            }
        
        total_accuracy = sum(result.get("accuracy", 0) for result in self.session_results)
        total_wpm = sum(result.get("wpm", 0) for result in self.session_results)
        
        return {
            "duration_minutes": duration_minutes,
            "items_completed": total_items,
            "average_accuracy": total_accuracy / total_items,
            "average_wpm": total_wpm / total_items,
            "completion_percentage": (total_items / len(self.study_items)) * 100 if self.study_items else 0,
            "date": self.end_time.strftime("%Y-%m-%d %H:%M")
        }
    
    def get_next_item(self) -> Optional[StudyItem]:
        """Get the next item in sequence"""
        if not self.study_items or self.current_index >= len(self.study_items):
            return None
        
        item = self.study_items[self.current_index]
        self.current_index += 1
        return item
    
    def peek_progress(self) -> Tuple[int, int]:
        """Get the current progress (current_index, total_items)"""
        return self.current_index, len(self.study_items)
    
    def record_result(self, result: Dict[str, Any]) -> None:
        """Record the result of a practice challenge"""
        self.session_results.append(result)
    
    def restart(self) -> None:
        """Restart practice from the beginning"""
        self.current_index = 0
    
    def shuffle_remaining(self) -> None:
        """Shuffle the remaining items"""
        if self.current_index < len(self.study_items):
            remaining = self.study_items[self.current_index:]
            random.shuffle(remaining)
            self.study_items[self.current_index:] = remaining
    
    def get_challenge_for_current_item(self) -> Optional[TypingChallenge]:
        """Get a typing challenge for the current item"""
        if not self.study_items or self.current_index >= len(self.study_items):
            return None
        
        item = self.study_items[self.current_index - 1]  # Use the item we just got
        challenge = TypingChallenge(item)
        challenge.start()
        return challenge
    
    def skip_item(self) -> None:
        """Skip the current item"""
        if self.current_index < len(self.study_items):
            self.current_index += 1
    
    def go_back(self) -> Optional[StudyItem]:
        """Go back to the previous item"""
        if self.current_index > 1:
            self.current_index -= 2  # Go back two steps (one to undo increment, one to go back)
            return self.get_next_item()
        return None
    
    def items_left(self) -> int:
        """Get the number of items left to practice"""
        return max(0, len(self.study_items) - self.current_index)
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get the results recorded so far"""
        return self.session_results