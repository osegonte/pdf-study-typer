# integration/challenge_generator.py

import random
from typing import List, Dict, Any, Optional
from datetime import datetime

from parser.study_item import StudyItem, StudyItemType


class TypingChallenge:
    """Represents a typing challenge based on a study item"""
    
    def __init__(self, study_item: StudyItem):
        self.study_item = study_item
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.user_input: str = ""
        self.accuracy: float = 0.0
        self.wpm: float = 0.0  # Words per minute
        self.completed: bool = False
    
    def start(self) -> None:
        """Start the challenge"""
        self.start_time = datetime.now()
    
    def complete(self, user_input: str) -> Dict[str, Any]:
        """Complete the challenge and calculate performance metrics"""
        self.end_time = datetime.now()
        self.user_input = user_input
        self.completed = True
        
        # Calculate accuracy
        self.accuracy = self._calculate_accuracy(user_input)
        
        # Calculate words per minute
        if self.end_time and self.start_time:
            time_taken = (self.end_time - self.start_time).total_seconds() / 60.0  # in minutes
            num_words = len(self.study_item.answer.split())
            self.wpm = num_words / time_taken if time_taken > 0 else 0
        
        return self.get_results()
    
    def get_results(self) -> Dict[str, Any]:
        """Get the challenge results"""
        if not self.completed:
            return {"status": "incomplete"}
        
        return {
            "item_id": self.study_item.id,
            "accuracy": self.accuracy,
            "wpm": self.wpm,
            "time_taken": (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0,
            "expected": self.study_item.answer,
            "actual": self.user_input
        }
    
    def _calculate_accuracy(self, user_input: str) -> float:
        """Calculate typing accuracy"""
        expected = self.study_item.answer
        
        # Simple character-by-character comparison
        if not expected:
            return 1.0  # Empty expected answer
        
        matches = sum(1 for a, b in zip(user_input, expected) if a == b)
        return matches / len(expected)


class ChallengeGenerator:
    """Generates typing challenges from study items"""
    
    def __init__(self, study_items: List[StudyItem] = None):
        self.study_items = study_items or []
        self.current_challenge: Optional[TypingChallenge] = None
    
    def add_items(self, items: List[StudyItem]) -> None:
        """Add study items to the generator"""
        self.study_items.extend(items)
    
    def get_random_challenge(self) -> Optional[TypingChallenge]:
        """Get a random typing challenge"""
        if not self.study_items:
            return None
        
        item = random.choice(self.study_items)
        self.current_challenge = TypingChallenge(item)
        return self.current_challenge
    
    def get_challenge_by_type(self, item_type: StudyItemType) -> Optional[TypingChallenge]:
        """Get a challenge for a specific item type"""
        items = [item for item in self.study_items if item.item_type == item_type]
        if not items:
            return None
        
        item = random.choice(items)
        self.current_challenge = TypingChallenge(item)
        return self.current_challenge
    
    def get_challenge_by_difficulty(self, difficulty: float) -> Optional[TypingChallenge]:
        """Get a challenge with a specific difficulty level"""
        # Group items by difficulty
        easy = [item for item in self.study_items if item.get_difficulty_score() < 0.3]
        medium = [item for item in self.study_items if 0.3 <= item.get_difficulty_score() < 0.7]
        hard = [item for item in self.study_items if item.get_difficulty_score() >= 0.7]
        
        # Select item pool based on requested difficulty
        if difficulty < 0.3 and easy:
            pool = easy
        elif difficulty < 0.7 and medium:
            pool = medium
        elif hard:
            pool = hard
        else:
            # Fallback to all items if no items match the criteria
            pool = self.study_items
        
        if not pool:
            return None
        
        item = random.choice(pool)
        self.current_challenge = TypingChallenge(item)
        return self.current_challenge


if __name__ == "__main__":
    # Test the challenge generator
    from parser.content_parser import PDFStudyExtractor
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFStudyExtractor(pdf_path)
        extractor.process()
        items = extractor.get_study_items()
        
        generator = ChallengeGenerator(items)
        challenge = generator.get_random_challenge()
        
        if challenge:
            print(f"Challenge prompt: {challenge.study_item.prompt}")
            print(f"Expected answer: {challenge.study_item.answer}")
            
            # Simulate typing
            challenge.start()
            # In a real app, the user would type the answer
            simulated_input = challenge.study_item.answer[:len(challenge.study_item.answer)//2]  # Simulate typing half correctly
            results = challenge.complete(simulated_input)
            
            print(f"Accuracy: {results['accuracy']*100:.1f}%")
            print(f"WPM: {results['wpm']:.1f}")
            print(f"Time taken: {results['time_taken']:.2f} seconds")
    else:
        print("Usage: python challenge_generator.py <path_to_pdf>")