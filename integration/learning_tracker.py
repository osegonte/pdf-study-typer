# integration/learning_tracker.py

import os
import json
from datetime import datetime, timedelta
import math
import random
from typing import List, Dict, Any, Optional, Tuple

from parser.study_item import StudyItem, StudyItemCollection


class SpacedRepetitionSystem:
    """Implements a spaced repetition system for optimizing learning"""
    
    def __init__(self, study_items: List[StudyItem] = None):
        self.study_items = study_items or []
        self.session_history: List[Dict[str, Any]] = []
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def add_items(self, items: List[StudyItem]) -> None:
        """Add study items to the system"""
        self.study_items.extend(items)
    
    def get_next_item(self) -> Optional[StudyItem]:
        """Get the next study item based on spaced repetition algorithm"""
        if not self.study_items:
            return None
        
        # Calculate priority for each item
        items_with_priority: List[Tuple[StudyItem, float]] = []
        now = datetime.now()
        
        for item in self.study_items:
            # Calculate time factor
            last_studied = getattr(item, 'last_studied', None)
            if last_studied is None:
                time_factor = 10.0  # High priority for new items
            else:
                # Calculate days since last studied
                days_since = (now - last_studied).days
                # Use SM-2 algorithm spacing
                ideal_interval = self._calculate_interval(item.mastery)
                time_factor = days_since / ideal_interval if ideal_interval > 0 else 10.0
            
            # Calculate final priority
            priority = time_factor * (1.0 - item.mastery) * item.importance
            items_with_priority.append((item, priority))
        
        # Sort by priority (highest first)
        items_with_priority.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness to avoid repetitive studying
        if random.random() < 0.1:  # 10% chance of randomization
            return random.choice(self.study_items)
        
        # Return highest priority item
        return items_with_priority[0][0]
    
    def update_item_mastery(self, item_id: str, performance: float) -> None:
        """Update the mastery level based on typing performance
        
        Args:
            item_id: ID of the study item
            performance: Score between 0.0 and 1.0 (typing accuracy)
        """
        for item in self.study_items:
            if item.id == item_id:
                # Update mastery level
                # Use a weighted average to smooth out changes
                if performance >= 0.95:  # Almost perfect performance
                    new_mastery = item.mastery * 0.7 + 0.3 * 1.0
                elif performance >= 0.8:  # Good performance
                    new_mastery = item.mastery * 0.8 + 0.2 * 0.9
                elif performance >= 0.6:  # Okay performance
                    new_mastery = item.mastery * 0.8 + 0.2 * 0.7
                else:  # Poor performance
                    new_mastery = item.mastery * 0.5 + 0.5 * 0.3
                
                # Ensure mastery stays between 0 and 1
                item.mastery = max(0.0, min(1.0, new_mastery))
                item.last_studied = datetime.now()
                
                # Record in session history
                self.session_history.append({
                    "item_id": item_id,
                    "timestamp": datetime.now().isoformat(),
                    "performance": performance,
                    "new_mastery": item.mastery
                })
                
                break
    
    def _calculate_interval(self, mastery: float) -> float:
        """Calculate ideal interval in days based on mastery level
        
        Uses a modified version of the SM-2 algorithm from SuperMemo
        """
        if mastery < 0.3:
            return 1.0  # Review daily
        elif mastery < 0.5:
            return 3.0  # Review every 3 days
        elif mastery < 0.7:
            return 7.0  # Review weekly
        elif mastery < 0.9:
            return 14.0  # Review every 2 weeks
        else:
            return 30.0  # Review monthly
    
    def save_progress(self, filename: str = "study_progress") -> str:
        """Save study progress to a file"""
        data = {
            "items": [item.to_dict() for item in self.study_items],
            "session_history": self.session_history,
            "metadata": {
                "date_saved": datetime.now().isoformat(),
                "total_items": len(self.study_items)
            }
        }
        
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def load_progress(self, filename: str = "study_progress") -> bool:
        """Load study progress from a file"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            # Load study items
            self.study_items = []
            for item_data in data.get("items", []):
                item = StudyItem.from_dict(item_data)
                self.study_items.append(item)
            
            # Load session history
            self.session_history = data.get("session_history", [])
            
            return True
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading progress: {str(e)}")
            return False
    
    def get_due_items(self) -> List[StudyItem]:
        """Get all items that are due for review"""
        due_items = []
        now = datetime.now()
        
        for item in self.study_items:
            last_studied = getattr(item, 'last_studied', None)
            if last_studied is None:
                # New item, never studied
                due_items.append(item)
                continue
            
            # Convert datetime string to datetime object if needed
            if isinstance(last_studied, str):
                try:
                    last_studied = datetime.fromisoformat(last_studied)
                except ValueError:
                    # Invalid datetime string, consider it as never studied
                    due_items.append(item)
                    continue
            
            # Calculate if the item is due
            days_since = (now - last_studied).days
            ideal_interval = self._calculate_interval(item.mastery)
            
            if days_since >= ideal_interval:
                due_items.append(item)
        
        return due_items
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        if not self.study_items:
            return {
                "total_items": 0,
                "mastered_items": 0,
                "mastery_percentage": 0,
                "average_mastery": 0
            }
        
        mastered_items = sum(1 for item in self.study_items if item.mastery >= 0.8)
        average_mastery = sum(item.mastery for item in self.study_items) / len(self.study_items)
        
        return {
            "total_items": len(self.study_items),
            "mastered_items": mastered_items,
            "mastery_percentage": (mastered_items / len(self.study_items)) * 100,
            "average_mastery": average_mastery
        }


class LearningTracker:
    """Tracks learning progress and provides analytics"""
    
    def __init__(self):
        self.spaced_repetition = SpacedRepetitionSystem()
        self.session_stats: Dict[str, Any] = {
            "start_time": None,
            "items_studied": 0,
            "correct_items": 0,
            "total_accuracy": 0,
            "total_wpm": 0
        }
    
    def start_session(self) -> None:
        """Start a new study session"""
        self.session_stats = {
            "start_time": datetime.now(),
            "items_studied": 0,
            "correct_items": 0,
            "total_accuracy": 0,
            "total_wpm": 0
        }
    
    def record_challenge_result(self, results: Dict[str, Any]) -> None:
        """Record the results of a typing challenge"""
        self.session_stats["items_studied"] += 1
        self.session_stats["total_accuracy"] += results.get("accuracy", 0)
        self.session_stats["total_wpm"] += results.get("wpm", 0)
        
        if results.get("accuracy", 0) >= 0.8:
            self.session_stats["correct_items"] += 1
        
        # Update spaced repetition system
        self.spaced_repetition.update_item_mastery(
            results.get("item_id", ""),
            results.get("accuracy", 0)
        )
    
    def end_session(self) -> Dict[str, Any]:
        """End the current study session and get stats"""
        end_time = datetime.now()
        
        if self.session_stats["start_time"] is None:
            duration = 0
        else:
            duration = (end_time - self.session_stats["start_time"]).total_seconds() / 60.0
        
        items_studied = self.session_stats["items_studied"]
        
        session_summary = {
            "duration_minutes": duration,
            "items_studied": items_studied,
            "correct_items": self.session_stats["correct_items"],
            "accuracy_percentage": (self.session_stats["total_accuracy"] / items_studied * 100) if items_studied > 0 else 0,
            "average_wpm": (self.session_stats["total_wpm"] / items_studied) if items_studied > 0 else 0,
            "date": end_time.strftime("%Y-%m-%d %H:%M")
        }
        
        # Reset session stats
        self.session_stats = {
            "start_time": None,
            "items_studied": 0,
            "correct_items": 0,
            "total_accuracy": 0,
            "total_wpm": 0
        }
        
        return session_summary
    
    def load_study_items(self, items: List[StudyItem]) -> None:
        """Load study items into the tracker"""
        self.spaced_repetition.add_items(items)
    
    def get_next_item(self) -> Optional[StudyItem]:
        """Get the next study item based on spaced repetition"""
        return self.spaced_repetition.get_next_item()
    
    def save_progress(self, filename: str = "learning_progress") -> str:
        """Save learning progress to a file"""
        return self.spaced_repetition.save_progress(filename)
    
    def load_progress(self, filename: str = "learning_progress") -> bool:
        """Load learning progress from a file"""
        return self.spaced_repetition.load_progress(filename)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return self.spaced_repetition.get_learning_stats()
    
    def get_due_items_count(self) -> int:
        """Get the number of items due for review"""
        return len(self.spaced_repetition.get_due_items())


if __name__ == "__main__":
    # Test the learning tracker
    from parser.content_parser import PDFStudyExtractor
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFStudyExtractor(pdf_path)
        extractor.process()
        items = extractor.get_study_items()
        
        tracker = LearningTracker()
        tracker.load_study_items(items)
        
        # Simulate a study session
        tracker.start_session()
        
        for _ in range(5):  # Study 5 items
            item = tracker.get_next_item()
            if item:
                print(f"Studying: {item.prompt}")
                # Simulate a random performance
                accuracy = random.uniform(0.5, 1.0)
                wpm = random.uniform(20, 60)
                
                tracker.record_challenge_result({
                    "item_id": item.id,
                    "accuracy": accuracy,
                    "wpm": wpm
                })
        
        # End session and get stats
        stats = tracker.end_session()
        print("\nSession Summary:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Save progress
        progress_path = tracker.save_progress()
        print(f"\nProgress saved to: {progress_path}")
        
# integration/learning_tracker.py (continued)
        # Get learning stats
        learning_stats = tracker.get_learning_stats()
        print("\nLearning Statistics:")
        for key, value in learning_stats.items():
            print(f"{key}: {value}")
        
        # Get due items count
        due_count = tracker.get_due_items_count()
        print(f"\nItems due for review: {due_count}")
    else:
        print("Usage: python learning_tracker.py <path_to_pdf>")