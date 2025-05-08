# integration/study_formatter.py

from typing import List, Dict, Any
import json
import os

from parser.study_item import StudyItem, StudyItemCollection


class StudyFormatter:
    """Formats study items for use in the typing trainer"""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def format_for_taipo(self, items: List[StudyItem]) -> List[Dict[str, Any]]:
        """Format study items for Taipo's prompt system"""
        formatted_items = []
        
        for item in items:
            # For each item, create a formatted structure
            # that matches Taipo's PromptChunks format
            
            # Split answer into individual characters for displayed
            displayed = [char for char in item.answer]
            
            # For typed, we'll use the same since we want users to type exactly what they see
            typed = displayed.copy()
            
            formatted_items.append({
                "displayed": displayed,
                "typed": typed,
                "original_id": item.id,
                "item_type": item.item_type.value,
                "prompt": item.prompt,
                "context": item.context,
                "importance": item.importance,
                "mastery": item.mastery
            })
        
        return formatted_items
    
    def save_taipo_format(self, items: List[StudyItem], filename: str = "study_content") -> str:
        """Save items in Taipo format to a JSON file"""
        formatted = self.format_for_taipo(items)
        
        # Prepare full data structure
        data = {
            "study_items": formatted,
            "metadata": {
                "count": len(formatted),
                "version": "1.0"
            }
        }
        
        # Save to file
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def convert_to_word_list(self, items: List[StudyItem], filename: str = "wordlist") -> str:
        """Convert study items to Taipo word list format"""
        # Create text file with one item per line
        content = ""
        
        for item in items:
            content += item.answer + "\n"
        
        # Save to file
        filepath = os.path.join(self.output_dir, f"{filename}.jp.txt")
        with open(filepath, "w") as f:
            f.write(content)
        
        return filepath


if __name__ == "__main__":
    # Test the formatter
    from parser.content_parser import PDFStudyExtractor
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFStudyExtractor(pdf_path)
        extractor.process()
        items = extractor.get_study_items()
        
        formatter = StudyFormatter()
        taipo_path = formatter.save_taipo_format(items)
        wordlist_path = formatter.convert_to_word_list(items)
        
        print(f"Saved Taipo format to: {taipo_path}")
        print(f"Saved word list to: {wordlist_path}")
    else:
        print("Usage: python study_formatter.py <path_to_pdf>")