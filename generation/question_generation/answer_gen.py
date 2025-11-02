import requests
import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

class AnswerGenerator:
    def __init__(self, 
                 api_key: str = None,
                 model: str = None):
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found. Please set it in .env file or pass as parameter.")
        
        # Get model from environment or parameter
        self.model = model or os.getenv("DEFAULT_MODEL", "mistralai/mistral-7b-instruct")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://yourdomain.com",
            "Content-Type": "application/json"
        }
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def _call_openrouter(self, prompt: str) -> str:
        """Make API call to OpenRouter for answer generation"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert educator creating model answers for academic questions."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            res = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)

            if res.status_code != 200:
                print("ERROR: OpenRouter Error Response:")
                print(res.status_code, res.text)
                raise Exception(f"OpenRouter error: {res.status_code}")

            data = res.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.Timeout:
            print("TIMEOUT: API call timed out after 60 seconds")
            raise Exception("API timeout - try again later")
        except requests.exceptions.JSONDecodeError:
            print("ERROR: Failed to decode JSON. Raw response:")
            print(res.text)
            raise Exception("OpenRouter response was not valid JSON.")
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            raise

    def generate_answer(self, question: str, chunk: str, bloom_level: str, marks: int) -> str:
        """Generate an answer for the given question based on the content chunk"""
        
        # Create answer generation prompt based on Bloom's level and marks
        answer_prompt = self._create_answer_prompt(question, chunk, bloom_level, marks)
        
        try:
            answer_text = self._call_openrouter(answer_prompt)
            return self._clean_answer(answer_text)
        except Exception as e:
            print(f"ERROR: Error generating answer: {e}")
            return "Answer generation failed. Please review manually."
    
    def _create_answer_prompt(self, question: str, chunk: str, bloom_level: str, marks: int) -> str:
        """Create a tailored prompt for answer generation based on Bloom's taxonomy"""
        
        base_prompt = f"""You are an expert educator creating model answers for academic questions.

Question: {question}

Source Content: {chunk}

Bloom's Taxonomy Level: {bloom_level}
Marks: {marks}

Please provide a comprehensive, accurate answer that:
1. Directly addresses the question
2. Uses information from the source content
3. Matches the cognitive level ({bloom_level})
4. Is appropriate for the mark allocation ({marks} marks)
5. Is clear, well-structured, and educational

Answer:"""

        # Add specific instructions based on Bloom's level
        if bloom_level == "Remember":
            base_prompt += "\n\nFocus on: Factual recall, definitions, and basic information."
        elif bloom_level == "Understand":
            base_prompt += "\n\nFocus on: Explaining concepts, relationships, and comprehension."
        elif bloom_level == "Apply":
            base_prompt += "\n\nFocus on: Practical application, problem-solving, and implementation."
        elif bloom_level == "Analyze":
            base_prompt += "\n\nFocus on: Breaking down components, comparing, and examining structure."
        elif bloom_level == "Evaluate":
            base_prompt += "\n\nFocus on: Making judgments, assessing effectiveness, and critical evaluation."
        elif bloom_level == "Create":
            base_prompt += "\n\nFocus on: Designing solutions, creating new approaches, and synthesis."
        
        return base_prompt
    
    def _clean_answer(self, text: str) -> str:
        """Clean and format the generated answer"""
        text = text.strip()
        
        # Remove common AI model artifacts
        artifacts_to_remove = [
            "<s>", "</s>", "[OUT]", "[/OUT]", "<s> [OUT]", "[/OUT] </s>",
            "**Answer:**", "**Model Answer:**", "Answer:", "Model Answer:", "Response:",
            "<|im_start|>", "<|im_end|>", "[INST]", "[/INST]"
        ]
        
        for artifact in artifacts_to_remove:
            text = text.replace(artifact, "").strip()
        
        # Remove any remaining XML-like tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[[^\]]+\]', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Remove italic
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If the text is too short or looks like an artifact, return a default
        if len(text) < 10 or text.startswith('<') or text.startswith('['):
            return "Answer generation failed. Please review manually."
        
        # Ensure proper ending
        if not text.endswith('.') and not text.endswith('!') and not text.endswith('?'):
            text += '.'
            
        return text
