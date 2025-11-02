"""
Image Association Module for Question Generation Pipeline
Associates extracted images with content topics/chunks
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from docx import Document


class ImageAssociator:
    """Associates images from DOCX with content topics/chunks"""
    
    def __init__(self, docx_path: str, output_dir: str = "answer_key_gen"):
        self.docx_path = docx_path
        self.output_dir = Path(output_dir)
        self.diagrams_dir = self.output_dir / "diagrams"
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)
        
        # Store extracted images with metadata
        self.extracted_images = []
        self.doc = None
        
        # Try to open DOCX
        try:
            self.doc = Document(docx_path)
            self._extract_all_images()
        except Exception as e:
            print(f"Warning: Could not open DOCX {docx_path}: {e}")
            self.doc = None

    def _extract_all_images(self):
        """Extract all images from DOCX and store with metadata"""
        if not self.doc:
            return
            
        self.extracted_images = []
        
        # Extract images from DOCX
        for rel in self.doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    # Get image data
                    image_data = rel.target_part.blob
                    
                    # Check image size - skip very small images (likely symbols/icons)
                    if len(image_data) < 20000:  # Skip images smaller than 20KB
                        print(f"Skipping small image (likely symbol/icon): {len(image_data)} bytes")
                        continue
                    
                    # Try to get actual image dimensions to filter out text snippets
                    try:
                        from PIL import Image
                        import io
                        img_obj = Image.open(io.BytesIO(image_data))
                        width, height = img_obj.size
                        
                        # Skip images that are too small (likely text snippets or icons)
                        if width < 200 or height < 200:
                            print(f"Skipping small dimension image: {width}x{height} pixels")
                            continue
                            
                        # Update size with actual dimensions
                        actual_size = (width, height)
                        img_obj.close()
                    except:
                        # If we can't get dimensions, use default size
                        actual_size = (200, 200)
                    
                    # Get image context from surrounding paragraphs
                    context = self._get_image_context_docx(rel)
                    
                    # Save image
                    img_filename = f"diagram_{len(self.extracted_images)}.png"
                    img_path = self.diagrams_dir / img_filename
                    
                    with open(img_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Store image metadata
                    self.extracted_images.append({
                        "path": str(img_path),
                        "page": 0,  # DOCX doesn't have pages
                        "context": context,
                        "filename": img_filename,
                        "used": False,
                        "size": actual_size  # Use actual dimensions
                    })
                    
                    print(f"Extracted image: {img_filename} ({len(image_data)} bytes)")
                    
                except Exception as e:
                    print(f"Warning: Could not extract image: {e}")
                    continue

    def _get_image_context_docx(self, rel) -> str:
        """Get text context around an image in DOCX"""
        try:
            # Get all paragraphs from the document
            paragraphs = []
            for paragraph in self.doc.paragraphs:
                paragraphs.append(paragraph.text)
            
            # Return the full document text as context for now
            # In a more sophisticated implementation, we could
            # find the specific location of the image and get nearby text
            return " ".join(paragraphs)
        except:
            return ""

    def find_image_for_topic(self, topic: str, content: str, page_range: Optional[Tuple[int, int]] = None) -> Optional[Dict]:
        """
        Find the most relevant image for a given topic/content
        
        Args:
            topic: Topic name or title
            content: Content text associated with the topic
            page_range: Optional tuple (start_page, end_page) to limit search
            
        Returns:
            Image metadata dict or None if no match
        """
        if not self.extracted_images:
            return None
        
        # Filter out already used images
        available_images = [img for img in self.extracted_images if not img['used']]
        
        if not available_images:
            return None
        
        # Combine topic and content for keyword extraction
        search_text = f"{topic} {content}"
        search_words = set(re.findall(r'\b\w+\b', search_text.lower()))
        
        best_image = None
        best_score = 0
        
        for img in available_images:
            # Calculate score based on context similarity
            context_words = set(re.findall(r'\b\w+\b', img['context'].lower()))
            
            # Simple scoring: count word overlaps
            overlap = len(search_words.intersection(context_words))
            total_words = len(search_words.union(context_words))
            
            if total_words > 0:
                score = overlap / total_words
            else:
                score = 0.0
            
            if score > best_score:
                best_score = score
                best_image = img
        
        # Only return if score is above threshold
        if best_score > 0.1:  # Minimum relevance threshold
            best_image['used'] = True  # Mark as used
            return best_image
        
        return None

    def find_image_for_question(self, question_text: str, answer_text: str = "", 
                              topic: str = "", content: str = "", 
                              page_range: Optional[Tuple[int, int]] = None) -> Optional[Dict]:
        """
        Find the most relevant image for a specific question using enhanced matching
        
        Args:
            question_text: The actual question text
            answer_text: The answer text (if available)
            topic: Topic name
            content: Content text
            page_range: Optional page range to search
            
        Returns:
            Image metadata dict or None if no match
        """
        if not self.extracted_images:
            return None
        
        # Filter out already used images
        available_images = [img for img in self.extracted_images if not img['used']]
        
        if not available_images:
            return None
        
        # Enhanced keyword extraction from question and answer
        question_words = set(re.findall(r'\b\w+\b', question_text.lower()))
        answer_words = set(re.findall(r'\b\w+\b', answer_text.lower())) if answer_text else set()
        topic_words = set(re.findall(r'\b\w+\b', topic.lower())) if topic else set()
        content_words = set(re.findall(r'\b\w+\b', content.lower())) if content else set()
        
        # Combine all keywords with different weights
        all_keywords = question_words.union(answer_words).union(topic_words).union(content_words)
        
        best_image = None
        best_score = 0
        
        for img in available_images:
            # Calculate enhanced relevance score
            context_words = set(re.findall(r'\b\w+\b', img['context'].lower()))
            
            # Multi-factor scoring
            score = 0
            
            # 1. Question text matching (highest weight)
            question_overlap = len(question_words.intersection(context_words))
            if len(question_words) > 0:
                score += (question_overlap / len(question_words)) * 0.4
            
            # 2. Answer text matching (high weight)
            if answer_words:
                answer_overlap = len(answer_words.intersection(context_words))
                score += (answer_overlap / len(answer_words)) * 0.3
            
            # 3. Topic matching (medium weight)
            if topic_words:
                topic_overlap = len(topic_words.intersection(context_words))
                score += (topic_overlap / len(topic_words)) * 0.2
            
            # 4. Content matching (lower weight)
            if content_words:
                content_overlap = len(content_words.intersection(context_words))
                score += (content_overlap / len(content_words)) * 0.1
            
            # 5. Visual similarity bonus (if image has good dimensions)
            if 'size' in img:
                width, height = img['size']
                # Prefer images that are reasonable size (not too small or too large)
                if 200 <= width <= 2000 and 200 <= height <= 2000:
                    score += 0.05
            
            if score > best_score:
                best_score = score
                best_image = img
        
        # Only return if score is above enhanced threshold
        if best_score > 0.15:  # Higher threshold for better quality
            best_image['used'] = True  # Mark as used
            return best_image
        
        return None

    def associate_image_with_question(self, question_id: str, question_text: str, 
                                    answer_text: str = "", topic: str = "", 
                                    content: str = "", page_range: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """
        Associate an image with a specific question using enhanced matching
        
        Args:
            question_id: Question identifier (e.g., "Q1", "Q4")
            question_text: The actual question text
            answer_text: The answer text (if available)
            topic: Topic name
            content: Content text
            page_range: Optional page range to search
            
        Returns:
            Relative path to image or None
        """
        # Enhanced matching using question text and answer
        image = self.find_image_for_question(question_text, answer_text, topic, content, page_range)
        
        if image:
            # Create a more descriptive filename based on question content
            safe_question = re.sub(r'[^\w\s-]', '', question_text)[:30]  # Clean question text
            safe_question = re.sub(r'[-\s]+', '_', safe_question)
            
            new_filename = f"diagram_{question_id}_{safe_question}.png"
            new_path = self.diagrams_dir / new_filename
            
            # Rename the file
            try:
                os.rename(image['path'], str(new_path))
                image['path'] = str(new_path)
                image['filename'] = new_filename
            except:
                pass  # Keep original if rename fails
            
            # Return relative path for JSON
            return f"./answer_key_gen/diagrams/{new_filename}"
        
        return None

    def get_available_images(self) -> List[Dict]:
        """Get list of all extracted images"""
        return self.extracted_images.copy()

    def reset_usage_flags(self):
        """Reset usage flags for all images (useful for re-processing)"""
        for img in self.extracted_images:
            img['used'] = False

    def __del__(self):
        """Clean up DOCX document"""
        # DOCX doesn't need explicit cleanup
        pass