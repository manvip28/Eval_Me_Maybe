from typing import Dict, List
import requests
import re
import os
from .ImageExtractor import TextbookImageExtractor
  # Your image extractor class

class ContentGenerator:
    def __init__(self, 
                 api_key: str,
                 model: str = "mistralai/mistral-7b-instruct",
                 textbook_path: str = None):
        """
        Initialize with API key and textbook PDF path
        Args:
            api_key: Your OpenRouter API key
            model: Model to use for generation
            textbook_path: Path to textbook PDF for image extraction
        """
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://yourdomain.com",
            "Content-Type": "application/json"
        }
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.image_extractor = TextbookImageExtractor(textbook_path) if textbook_path else None

    def generate_review_materials(self, approved_questions: List[Dict], style: str = "answer") -> Dict:
        """
        Generate complete review materials with images
        Args:
            approved_questions: List of question dicts with:
                - question: The question text
                - bloom: Bloom's level
                - marks: Question marks
                - keywords_used: List of keywords
                - chunk: Source text chunk
                - topic: Textbook topic/section
            style: Output style (answer|study_guide|presentation)
        Returns:
            Dictionary containing formatted content with images
        """
        outputs = []
        
        for q in approved_questions:
            # Generate base content
            prompt = self._build_prompt(q, style)
            response = self._call_openrouter(prompt)
            formatted_response = self.parse_response(response)
            
            # Enhance with textbook images if available
            print(self.image_extractor)
            if self.image_extractor:
                images = self.image_extractor.find_images_for_topic(q.get('topic', ''))
                print(q.get('topic', ''))
                formatted_response["textbook_images"] = [
                    {
                        "path": os.path.basename(img['path']),
                        "page": img['page'],
                        "context": img['context'][:200] + "...",
                        "relevance": round(img['score'], 2)
                    } for img in images[:2]  # Get top 2 images
                ]
            
            outputs.append(formatted_response)
            
        return {
            "content": outputs,
            "style": style,
            "total_questions": len(approved_questions)
        }

    def _build_prompt(self, question_data: Dict, style: str) -> str:
        """Construct the generation prompt"""
        return f"""
Generate content in EXACTLY this format:

### QUESTION
{question_data['question']}

### BLOOM_LEVEL
{question_data['bloom']} (MARKS: {question_data['marks']})

### CONTENT
[Using this source text: "{question_data['chunk'][:2000]}"]
• Create {1 if style == "presentation" else 2} paragraphs
• Bold key terms: {', '.join(f"**{kw}**" for kw in question_data['keywords_used'])}
• For "Analyze" level, include comparisons
• For "Create" level, propose solutions

### VISUALS
[Required: 3 image suggestions from this list]
1. TYPE: diagram|chart|timeline|comparison_table|infographic
   PURPOSE: [1 sentence]
2. TYPE: diagram|chart|timeline|comparison_table|infographic
   PURPOSE: [1 sentence]
3. TYPE: diagram|chart|timeline|comparison_table|infographic
   PURPOSE: [1 sentence]

### RULES
- Never deviate from this format
- Use bullet points, not numbered lists
- Keep paragraphs under 100 words
- Section headers must start with ###
"""

    def parse_response(self, response: str) -> Dict[str, any]:
        """Parse API response into structured format"""
        result = {
            "question": "",
            "bloom_level": "Unknown",
            "marks": 0,
            "content": "",
            "keywords": [],
            "visual_suggestions": [],
            "textbook_images": []  # Will be filled later
        }
        
        try:
            # Extract sections
            section_pattern = r'### ([A-Z_]+)\s*\n([\s\S]+?)(?=\n### |\Z)'
            sections = dict(re.findall(section_pattern, response))
            
            # Fill result fields
            result["question"] = sections.get('QUESTION', '').strip()
            
            bloom_section = sections.get('BLOOM_LEVEL', '')
            if bloom_section:
                result["bloom_level"] = bloom_section.split()[0]
                marks_match = re.search(r'MARKS:\s*(\d+)', bloom_section)
                if marks_match:
                    result["marks"] = int(marks_match.group(1))
            
            result["content"] = sections.get('CONTENT', '').strip()
            result["keywords"] = re.findall(r'\*\*(\w+)\*\*', result["content"])
            
            # Parse visual suggestions
            visuals_text = sections.get('VISUALS', '')
            visual_matches = re.finditer(
                r'(\d+)\. TYPE:\s*(\w+)\s*PURPOSE:\s*(.+)', 
                visuals_text
            )
            result["visual_suggestions"] = [
                {"type": m.group(2), "purpose": m.group(3).strip()}
                for m in visual_matches
            ][:3]
            
        except Exception as e:
            print(f"⚠️ Parsing error: {str(e)}")
            print(f"Problematic response:\n{response}")
        
        return result

    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API with error handling"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            res = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            raise


        