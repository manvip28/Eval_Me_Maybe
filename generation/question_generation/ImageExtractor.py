from typing import List, Dict
import os
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyMuPDF not installed. Install with: pip install PyMuPDF")


class TextbookImageExtractor:
    """Extract images from PDF textbook."""
    
    def __init__(self, pdf_path: str):
        """Initialize with PDF path."""
        self.pdf_path = pdf_path
        self.images_cache = []
        
        if not PDF_AVAILABLE:
            print("Warning: PyMuPDF not available. Image extraction disabled.")
            return
            
        try:
            # Open PDF and extract images
            doc = fitz.open(pdf_path)
            self._extract_images_from_pdf(doc)
            doc.close()
        except Exception as e:
            print(f"Warning: Could not extract images from PDF {pdf_path}: {e}")
            self.images_cache = []

    def _extract_images_from_pdf(self, doc):
        """Extract all images from the PDF and save them."""
        self.images_cache = []
        
        # Create output directory
        output_dir = Path(self.pdf_path).parent / "extracted_images"
        output_dir.mkdir(exist_ok=True)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get images on this page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Skip if not RGB/GRAY
                    if pix.n - pix.alpha < 4:
                        # Save image to file
                        img_filename = f"page_{page_num}_img_{img_index}.png"
                        img_path = output_dir / img_filename
                        
                        pix.save(str(img_path))
                        
                        # Get surrounding text for context
                        context = ""
                        try:
                            img_rects = page.get_image_rects(xref)
                            if img_rects:
                                img_rect = img_rects[0]
                                # Get text around the image
                                expanded_rect = fitz.Rect(
                                    img_rect.x0 - 50, img_rect.y0 - 50,
                                    img_rect.x1 + 50, img_rect.y1 + 50
                                )
                                context = page.get_textbox(expanded_rect)
                        except:
                            context = f"Image from page {page_num}"
                        
                        self.images_cache.append({
                            "path": str(img_path),
                            "page": page_num,
                            "context": context,
                            "score": 0.0
                        })
                        
                    pix = None
                    
                except Exception as e:
                    print(f"Warning: Could not extract image {img_index} from page {page_num}: {e}")
                    continue

    def find_images_for_topic(self, topic: str, 
                              num_images: int = 2,
                              min_score: float = 0.1) -> List[Dict]:
        """Find images relevant to the given topic."""
        if not self.images_cache:
            return []
        
        # Simple keyword matching
        topic_words = set(re.findall(r'\b\w+\b', topic.lower()))
        
        scored_images = []
        for img in self.images_cache:
            # Calculate simple relevance score
            context_words = set(re.findall(r'\b\w+\b', img['context'].lower()))
            
            # Count word overlaps
            overlap = len(topic_words.intersection(context_words))
            img['score'] = overlap / max(len(topic_words), 1)
            
            if img['score'] >= min_score:
                scored_images.append(img)
        
        # Sort by score and return top N
        scored_images.sort(key=lambda x: x['score'], reverse=True)
        return scored_images[:num_images]