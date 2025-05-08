# parser/study_item.py

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import json

class StudyItemType(Enum):
    DEFINITION = "definition"
    KEY_CONCEPT = "key_concept"
    FILL_IN_BLANK = "fill_in_blank"
    FORMULA = "formula"
    LIST = "list"


@dataclass
class StudyItem:
    """Represents a single study item extracted from a document"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""  # What the user will see as a prompt
    answer: str = ""  # The expected answer to type
    context: str = ""  # Section or chapter info
    item_type: StudyItemType = StudyItemType.KEY_CONCEPT
    importance: int = 5  # 1-10 importance score
    mastery: float = 0.0  # 0.0 to 1.0 mastery level
    last_studied: Optional[datetime] = None
    source_document: str = ""  # Source document name
    
    def get_difficulty_score(self) -> float:
        """Calculate how difficult this item is based on length, mastery, etc."""
        length_factor = len(self.answer) / 100  # Longer answers are harder
        mastery_factor = 1.0 - self.mastery    # Lower mastery means higher difficulty
        return (length_factor + mastery_factor) * self.importance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "answer": self.answer,
            "context": self.context,
            "item_type": self.item_type.value,
            "importance": self.importance,
            "mastery": self.mastery,
            "last_studied": self.last_studied.isoformat() if self.last_studied else None,
            "source_document": self.source_document
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudyItem':
        """Create a StudyItem from a dictionary"""
        # Convert string type back to enum
        item_type = StudyItemType(data.get("item_type", "key_concept"))
        
        # Handle the datetime conversion
        last_studied = None
        if data.get("last_studied"):
            try:
                last_studied = datetime.fromisoformat(data["last_studied"])
            except (ValueError, TypeError):
                pass
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            prompt=data.get("prompt", ""),
            answer=data.get("answer", ""),
            context=data.get("context", ""),
            item_type=item_type,
            importance=data.get("importance", 5),
            mastery=data.get("mastery", 0.0),
            last_studied=last_studied,
            source_document=data.get("source_document", "")
        )


class StudyItemCollection:
    """A collection of study items with save/load capabilities"""
    
    def __init__(self):
        self.items: List[StudyItem] = []
    
    def add_item(self, item: StudyItem) -> None:
        """Add a study item to the collection"""
        self.items.append(item)
    
    def add_items(self, items: List[StudyItem]) -> None:
        """Add multiple study items to the collection"""
        self.items.extend(items)
    
    def get_items(self) -> List[StudyItem]:
        """Get all study items"""
        return self.items
    
    def get_item_by_id(self, item_id: str) -> Optional[StudyItem]:
        """Get a study item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def save_to_file(self, filepath: str) -> None:
        """Save study items to a JSON file"""
        data = {
            "items": [item.to_dict() for item in self.items],
            "metadata": {
                "count": len(self.items),
                "date_created": datetime.now().isoformat()
            }
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'StudyItemCollection':
        """Load study items from a JSON file"""
        collection = cls()
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            items_data = data.get("items", [])
            for item_data in items_data:
                collection.add_item(StudyItem.from_dict(item_data))
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading study items: {str(e)}")
        
        return collection