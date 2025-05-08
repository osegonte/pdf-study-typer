# parser/text_parser.py

import re
import uuid
from typing import List, Dict, Any, Optional
from .study_item import StudyItem, StudyItemType
class TextParser:
    """Parser for extracting study items from plain text content"""
    
    def __init__(self, text: str = ""):
        self.text = text
        self.study_items: List[StudyItem] = []
    
    def set_text(self, text: str) -> 'TextParser':
        """Set the text content to parse"""
        self.text = text
        return self
    
    def parse(self) -> 'TextParser':
        """Parse the text to extract study items"""
        if not self.text:
            return self
        
        # Try different parsing methods based on content format
        if self._looks_like_qa_format():
            self._parse_qa_format()
        elif self._looks_like_definition_list():
            self._parse_definition_list()
        elif self._looks_like_bullet_list():
            self._parse_bullet_list()
        else:
            # Default parsing as simple lines
            self._parse_simple_lines()
        
        return self
    
    def _looks_like_qa_format(self) -> bool:
        """Check if the text looks like a Q&A format"""
        return bool(re.search(r'Q\s*:|Question\s*:', self.text, re.IGNORECASE) and 
                    re.search(r'A\s*:|Answer\s*:', self.text, re.IGNORECASE))
    
    def _looks_like_definition_list(self) -> bool:
        """Check if the text looks like a definition list"""
        # Look for patterns like "Term - Definition" or "Term: Definition"
        return bool(re.search(r'^[A-Z][a-zA-Z\s]{2,40}[\s]*[-:]\s', self.text, re.MULTILINE))
    
    def _looks_like_bullet_list(self) -> bool:
        """Check if the text looks like a bullet list"""
        # Look for bullet patterns like "• item" or "- item" or "* item"
        return bool(re.search(r'^[\s]*[•\-\*]\s', self.text, re.MULTILINE))
    
    def _parse_qa_format(self) -> None:
        """Parse text in Q&A format"""
        # Split by Q: or Question:
        qa_pattern = re.compile(r'(?:^|\n)(?:Q\s*:|Question\s*:)(.*?)(?:(?:\n)(?:A\s*:|Answer\s*:)(.*?)(?=(?:\n)(?:Q\s*:|Question\s*:)|$))', re.DOTALL)
        matches = qa_pattern.findall(self.text)
        
        for question, answer in matches:
            question = question.strip()
            answer = answer.strip()
            
            if question and answer:
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt=f"Q: {question}",
                    answer=answer,
                    context="Q&A",
                    item_type=StudyItemType.KEY_CONCEPT,
                    importance=7
                ))
    
    def _parse_definition_list(self) -> None:
        """Parse text as a list of definitions"""
        # Match both "Term - Definition" and "Term: Definition" patterns
        definition_pattern = re.compile(r'^([A-Z][a-zA-Z\s]{2,40})[\s]*[-:]\s+(.*?)(?=\n[A-Z]|$)', re.MULTILINE | re.DOTALL)
        matches = definition_pattern.findall(self.text)
        
        for term, definition in matches:
            term = term.strip()
            definition = definition.strip()
            
            if term and definition:
                # Create study item for term->definition
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt=f"Define the term: {term}",
                    answer=definition,
                    context="Terminology",
                    item_type=StudyItemType.DEFINITION,
                    importance=7
                ))
                
                # Create study item for definition->term
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt=f"What term is defined as: {definition}",
                    answer=term,
                    context="Terminology",
                    item_type=StudyItemType.DEFINITION,
                    importance=7
                ))
    
    def _parse_bullet_list(self) -> None:
        """Parse text as a bullet list"""
        # Match bullet points
        bullet_pattern = re.compile(r'^[\s]*[•\-\*]\s+(.*?)(?=\n[\s]*[•\-\*]|$)', re.MULTILINE | re.DOTALL)
        matches = bullet_pattern.findall(self.text)
        
        # First, collect all bullet points
        bullet_points = [match.strip() for match in matches if match.strip()]
        
        if bullet_points:
            # Create a list item from the bullet points
            list_text = "\n".join([f"• {point}" for point in bullet_points])
            
            self.study_items.append(StudyItem(
                id=str(uuid.uuid4()),
                prompt="Type this list in order:",
                answer=list_text,
                context="List",
                item_type=StudyItemType.LIST,
                importance=6
            ))
            
            # Also create individual items for each point
            for point in bullet_points:
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt="Type this item:",
                    answer=point,
                    context="List Item",
                    item_type=StudyItemType.KEY_CONCEPT,
                    importance=5
                ))
    
    def _parse_simple_lines(self) -> None:
        """Parse text as simple lines, each becoming a study item"""
        lines = self.text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line:
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt="Type this:",
                    answer=line,
                    context="Custom Content",
                    item_type=StudyItemType.KEY_CONCEPT,
                    importance=5
                ))
    
    def get_study_items(self) -> List[StudyItem]:
        """Return the extracted study items"""
        return self.study_items
    
    @classmethod
    def from_file(cls, file_path: str) -> 'TextParser':
        """Create a TextParser from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return cls(text)
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            return cls()


# Add the following methods to the main application class (PDFStudyTypingTrainer)
# to use the TextParser:

def _import_from_text(self):
    """Import study items from plain text"""
    text = self.bulk_text.get("1.0", tk.END).strip()
    
    if not text:
        messagebox.showwarning("Empty Input", "Please enter some text to import.")
        return
    
    # Use TextParser to extract study items
    from parser.text_parser import TextParser
    parser = TextParser(text)
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
        from parser.text_parser import TextParser
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