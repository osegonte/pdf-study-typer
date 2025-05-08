# integration/taipo_integration.py

import os
import json
import subprocess
from typing import List, Dict, Any, Optional

from parser.study_item import StudyItem


class TaipoIntegration:
    """Integration with Taipo typing game"""
    
    def __init__(self, taipo_path=None):
        # Try to find Taipo path
        self.taipo_path = taipo_path
        
        if not self.taipo_path:
            # Try common installation locations
            possible_paths = [
                "./taipo",  # Current directory
                os.path.expanduser("~/taipo"),  # Home directory
                os.path.expanduser("~/games/taipo"),  # Games directory
                "C:\\Program Files\\Taipo",  # Windows Program Files
                "/usr/local/bin/taipo",  # Linux
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.taipo_path = path
                    break
        
        # Create study content directory
        self.study_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "taipo")
        os.makedirs(self.study_dir, exist_ok=True)
    
    def is_taipo_available(self) -> bool:
        """Check if Taipo is available"""
        return self.taipo_path is not None and os.path.exists(self.taipo_path)
    
    def convert_to_taipo_format(self, study_items: List[StudyItem]) -> Dict[str, Any]:
        """Convert study items to Taipo format"""
        taipo_items = []
        
        for item in study_items:
            # Split answer into characters for displayed and typed
            displayed = []
            typed = []
            
            for char in item.answer:
                displayed.append(char)
                typed.append(char)
            
            taipo_items.append({
                "displayed": displayed,
                "typed": typed,
                "metadata": {
                    "id": item.id,
                    "prompt": item.prompt,
                    "type": item.item_type.value,
                    "importance": item.importance,
                    "mastery": item.mastery
                }
            })
        
        return {
            "study_items": taipo_items,
            "metadata": {
                "count": len(taipo_items),
                "version": "1.0",
                "mode": "study"
            }
        }
    
    def save_study_content(self, study_items: List[StudyItem], filename: str) -> str:
        """Save study items in Taipo format"""
        data = self.convert_to_taipo_format(study_items)
        
        # Generate filepath
        filepath = os.path.join(self.study_dir, f"{filename}.json")
        
        # Save to file
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def launch_taipo(self, content_file: str) -> bool:
        """Launch Taipo with the specified study content"""
        if not self.is_taipo_available():
            return False
        
        try:
            # Construct the command to launch Taipo
            # Assuming Taipo supports a command-line argument for study content
            cmd = [self.taipo_path, "--study-content", content_file]
            
            # Launch Taipo
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            print(f"Error launching Taipo: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the Taipo integration
    from parser.content_parser import PDFStudyExtractor
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFStudyExtractor(pdf_path)
        extractor.process()
        items = extractor.get_study_items()
        
        integration = TaipoIntegration()
        
        if integration.is_taipo_available():
            print(f"Taipo found at: {integration.taipo_path}")
            
            # Save study content
            content_file = integration.save_study_content(
                items, 
                os.path.splitext(os.path.basename(pdf_path))[0]
            )
            
            print(f"Saved study content to: {content_file}")
            
            # Launch Taipo
            success = integration.launch_taipo(content_file)
            
            if success:
                print("Taipo launched successfully!")
            else:
                print("Failed to launch Taipo.")
        else:
            print("Taipo not found.")
    else:
        print("Usage: python taipo_integration.py <path_to_pdf>")