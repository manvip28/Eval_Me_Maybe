import requests
import random
import os
from jinja2 import Template
from dotenv import load_dotenv
from typing import Dict, List
from .bloom_mapper import get_chunk
from .bloom_config import BLOOM_CONFIG
from .answer_gen import AnswerGenerator

# Load environment variables
load_dotenv()

class QuestionGenerator:
    def __init__(self, 
                 prompt_path: str = "generation/question_generation/prompt_engine/prompts.yaml",
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

        with open(prompt_path) as f:
            import yaml
            self.prompt_templates = yaml.safe_load(f)

        self.bloom_config = BLOOM_CONFIG
        self.answer_generator = AnswerGenerator(api_key=api_key, model=model)

    def _call_openrouter(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that creates academic questions."},
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


    def generate_question(self, topic: str, content: str, keywords: List[str]) -> Dict:
        bloom_level = self.select_bloom_level(len(content))
        possible_marks = self.bloom_config[bloom_level]["marks"]
        marks = random.choice(possible_marks)
        chunk = get_chunk(content, bloom_level, marks)

        # Prompt template render
        template_str = self.prompt_templates[bloom_level].get(str(marks))
        if not template_str:
            template_str = self.prompt_templates[bloom_level][max(map(int, self.prompt_templates[bloom_level].keys()))]

        prompt = Template(template_str).render(
            marks=marks,
            bloom=bloom_level,
            chunk=chunk,
            keywords=keywords
        )

        # Add variety and strictness to reduce duplicates and malformed outputs
        variety_instructions = [
            "Focus on a different aspect of the content.",
            "Ask about a specific application or example.",
            "Compare or contrast different concepts.",
            "Explain the relationship between key terms.",
            "Describe the process or steps involved."
        ]
        
        prompt += f"\n\nIMPORTANT: Output ONLY a single well-formed question sentence. {random.choice(variety_instructions)} Do not include any prefixes, tags, or formatting."

        # Single attempt only
        question_text = self._clean_question(self._call_openrouter(prompt))

        # If invalid, abort so caller can skip without extra calls
        if question_text == "Question generation failed. Please review manually.":
            raise ValueError("question_generation_failed")

        # Generate answer for the question
        answer_text = self.answer_generator.generate_answer(question_text, chunk, bloom_level, marks)

        # Use available keywords (should not be empty due to skip logic above)
        max_keywords = min(len(keywords), 2 if marks < 5 else 3)
        used_keywords = random.sample(keywords, max_keywords) if max_keywords > 0 else keywords[:1]

        return {
            "question": question_text,
            "answer": answer_text,
            "bloom": bloom_level,
            "marks": marks,
            "source_topic": topic,
            "keywords_used": used_keywords,
            "chunk":chunk,
            "approved": True,
            "feedback": None
        }


    def _clean_question(self, text: str) -> str:
        """Clean and format the generated question"""
        text = text.strip()
        
        # Remove common AI model artifacts
        artifacts_to_remove = [
            "<s>", "</s>", "[OUT]", "[/OUT]", "<s> [OUT]", "[/OUT] </s>",
            "**Question:**", "**Question (", "Question:", "Question (",
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
            return "Question generation failed. Please review manually."
        
        # Take only the first line if there are multiple lines
        first_line = text.split('\n')[0].strip()
        
        # Ensure it ends with a question mark if it looks like a question
        if any(first_line.lower().startswith(w) for w in ["what", "how", "why", "when", "where", "which", "explain", "describe", "compare", "design", "evaluate"]):
            if not first_line.endswith('?'):
                first_line += '?'
        else:
            # Allow statements for higher-order prompts; ensure punctuation
            if not first_line.endswith('.'):
                first_line += '.'
            
        return first_line

    def select_bloom_level(self, topic_length: int) -> str:
        if topic_length < 500:
            return "Remember"
        elif topic_length < 1500:
            return random.choice(["Remember", "Understand", "Apply"])
        else:
            weights = [1, 2, 3, 4, 2, 1]
            return random.choices(list(self.bloom_config.keys()), weights=weights, k=1)[0]

    def generate_for_topics(self, topics: Dict[str, str], keywords_dict: Dict[str, List[str]], questions_per_topic: int = 3) -> List[Dict]:
        questions = []
        total_questions = len(topics) * questions_per_topic
        current_question = 0
        generated_questions = set()  # Track generated questions to avoid duplicates
        
        for topic, content in topics.items():
            keywords = keywords_dict.get(topic, [])
            
            for i in range(questions_per_topic):
                current_question += 1
                
                try:
                    # Skip if no keywords available
                    if not keywords or len(keywords) == 0:
                        print(f"SKIP: No keywords available for topic: {topic[:30]}...")
                        continue
                    
                    # Add variety by shuffling keywords and adding randomness
                    shuffled_keywords = keywords.copy()
                    random.shuffle(shuffled_keywords)
                    
                    # Use different keyword subsets for variety
                    if len(keywords) > 2:
                        keyword_subset = random.sample(keywords, min(len(keywords), random.randint(2, 4)))
                    else:
                        keyword_subset = keywords
                    
                    
                    question = self.generate_question(topic, content, keyword_subset)
                    
                    # Simple duplicate check - skip if very similar question exists
                    question_lower = question['question'].lower().strip()
                    if any(question_lower in existing or existing in question_lower 
                           for existing in generated_questions if len(existing) > 20):
                        print(f"SKIP: Duplicate question detected, skipping...")
                        continue
                    
                    generated_questions.add(question_lower)
                    questions.append(question)
                except Exception as e:
                    print(f"ERROR: Failed to generate question {current_question}: {e}")
                    # Continue with next question instead of stopping
                    continue
        return questions