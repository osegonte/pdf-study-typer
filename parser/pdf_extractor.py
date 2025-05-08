# parser/pdf_extractor.py

import fitz  # PyMuPDF
import os
from typing import List, Dict, Any

class PDFExtractor:
    """Base class for PDF extraction, handling the raw text extraction"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_text = ""
        self.title = "Unknown"
        self.author = "Unknown"
        # Default scan area covers the whole page - adjust if needed
        self.scan_area = fitz.Rect(0, 0, 600, 850)
    
    def extract(self) -> 'PDFExtractor':
        """Extract text from PDF"""
        if not os.path.exists(self.pdf_path):
            print(f"File not found: {self.pdf_path}")
            return self
            
        try:
            with fitz.open(self.pdf_path) as doc:
                # Extract metadata
                self.title = doc.metadata.get("title", os.path.basename(self.pdf_path))
                self.author = doc.metadata.get("author", "Unknown")
                
                # Extract text from each page
                for page in doc:
                    # Get text within scan area
                    page_text = page.get_text("text", clip=self.scan_area)
                    self.raw_text += page_text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
        
        return self
    
    def get_text(self) -> str:
        """Get the extracted text"""
        if not self.raw_text:
            self.extract()
        return self.raw_text
    
    def get_title(self) -> str:
        """Get the document title"""
        return self.title
    
    def get_author(self) -> str:
        """Get the document author"""
        return self.author
    
    def set_scan_area(self, x0: float, y0: float, x1: float, y1: float) -> 'PDFExtractor':
        """Set the scan area for text extraction"""
        self.scan_area = fitz.Rect(x0, y0, x1, y1)
        return self


if __name__ == "__main__":
    # Test the extractor
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFExtractor(pdf_path)
        text = extractor.extract().get_text()
        print(f"Title: {extractor.get_title()}")
        print(f"Author: {extractor.get_author()}")
        print(f"Text length: {len(text)} characters")
        print("\nSample text:")
        print(text[:500] + "...")  # Print first 500 characters
    else:
        print("Usage: python pdf_extractor.py <path_to_pdf>")