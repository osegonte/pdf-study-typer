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