# study_content_extractor.py

import fitz  # PyMuPDF
import re
import uuid
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import os


class StudyItemType(Enum):
    DEFINITION = "definition"
    KEY_CONCEPT = "key_concept"
    FILL_IN_BLANK = "fill_in_blank"
    FORMULA = "formula"
    LIST = "list"


@dataclass
class StudyItem:
    id: str
    prompt: str  # What the user will type
    answer: str  # The expected answer
    context: str  # Section or chapter info
    item_type: StudyItemType
    importance: int  # 1-10 importance score
    mastery: float = 0.0  # 0.0 to 1.0


class PDFStudyExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_text = ""
        self.study_items: List[StudyItem] = []
        # Area picker, adjust as needed for academic content
        self.scan_area = fitz.Rect(0, 0, 600, 850)
        
    def extract(self) -> 'PDFStudyExtractor':
        """Extract text from PDF"""
        if not os.path.exists(self.pdf_path):
            return self
            
        with fitz.open(self.pdf_path) as doc:
            # Extract metadata for context
            self.title = doc.metadata.get("title", "Unknown")
            
            # Extract text from each page
            for page in doc:
                # Get text within scan area
                page_text = page.get_text("text", clip=self.scan_area)
                self.raw_text += page_text
                
        return self
    
    def process(self) -> 'PDFStudyExtractor':
        """Process the extracted text to identify study items"""
        if not self.raw_text:
            self.extract()
            
        # Extract different types of study content
        self._extract_definitions()
        self._extract_key_concepts()
        self._extract_formulas()
        self._extract_lists()
        
        return self
        
    def _extract_definitions(self):
        """Extract term-definition pairs"""
        # Pattern: Term: Definition or Term - Definition
        definition_patterns = [
            r'([A-Z][a-zA-Z\s]{2,40}):([^\.]+\.)',
            r'([A-Z][a-zA-Z\s]{2,40})\s-\s([^\.]+\.)'
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, self.raw_text)
            
            for term, definition in matches:
                term = term.strip()
                definition = definition.strip()
                
                # Create study items for both term->definition and definition->term
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt=f"Define the term: {term}",
                    answer=definition,
                    context="Terminology",
                    item_type=StudyItemType.DEFINITION,
                    importance=7
                ))
                
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt=f"What term is defined as: {definition}",
                    answer=term,
                    context="Terminology",
                    item_type=StudyItemType.DEFINITION,
                    importance=7
                ))
    
    def _extract_key_concepts(self):
        """Extract key concepts based on formatting hints or repetition"""
        # Look for sentences with key indicator phrases
        key_phrases = ["important", "key concept", "remember", "critical", "note that"]
        sentences = re.split(r'\.', self.raw_text)
        
        for sentence in sentences:
            for phrase in key_phrases:
                if phrase in sentence.lower():
                    # Found a potential key concept
                    concept = sentence.strip()
                    if len(concept) > 20:  # Ensure it's meaningful
                        self.study_items.append(StudyItem(
                            id=str(uuid.uuid4()),
                            prompt="Type this key concept:",
                            answer=concept,
                            context="Key Concepts",
                            item_type=StudyItemType.KEY_CONCEPT,
                            importance=8
                        ))
    
    def _extract_formulas(self):
        """Extract mathematical or scientific formulas"""
        # Look for text that appears to be formulas
        formula_pattern = r'([A-Za-z][\w]*)\s*=\s*([^\.]+)'
        matches = re.findall(formula_pattern, self.raw_text)
        
        for variable, formula in matches:
            formula_text = f"{variable} = {formula}"
            self.study_items.append(StudyItem(
                id=str(uuid.uuid4()),
                prompt=f"Type the formula for {variable}:",
                answer=formula_text,
                context="Formulas",
                item_type=StudyItemType.FORMULA,
                importance=9
            ))
    
    def _extract_lists(self):
        """Extract numbered or bulleted lists"""
        # Match numbered lists (e.g., "1. Item\n2. Item\n3. Item")
        list_pattern = r'((\d+\.\s*[^\n]+\n){2,})'
        matches = re.findall(list_pattern, self.raw_text)
        
        for match in matches:
            list_text = match[0].strip()
            if len(list_text) > 30:  # Ensure it's a meaningful list
                self.study_items.append(StudyItem(
                    id=str(uuid.uuid4()),
                    prompt="Type out this list in order:",
                    answer=list_text,
                    context="Lists",
                    item_type=StudyItemType.LIST,
                    importance=6
                ))
    
    def get_study_items(self) -> List[StudyItem]:
        """Return the extracted study items"""
        return self.study_items


if __name__ == "__main__":
    # Test the extractor
    import glob
    pdf_files = glob.glob("./input/*.pdf")
    for file in pdf_files:
        extractor = PDFStudyExtractor(file)
        extractor.process()
        items = extractor.get_study_items()
        print(f"Extracted {len(items)} study items from {file}")
        # Print first 3 items for preview
        for item in items[:3]:
            print(f"Type: {item.item_type.value}, Prompt: {item.prompt}")