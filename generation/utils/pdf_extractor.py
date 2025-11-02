import re
from collections import OrderedDict
from typing import OrderedDict as OrderedDictType

import pdfplumber


def is_topic_header(text: str) -> bool:
    """Return True if the line looks like a numbered topic header, e.g. '1.1 Title'."""
    pattern = r"^\d+(\.\d+)*\s+.+$"
    return bool(re.match(pattern, text.strip()))


def clean_header(text: str) -> str:
    """
    Cleans section headers like '1.1.   Cloud Computing' → '1.1 Cloud Computing'.

    Rules:
    - Normalize multiple spaces
    - Convert '1.1.' to '1.1' while preserving the section number
    - Return '<section_number> <title>' when parseable, else the original text
    """
    text = text.strip()

    # Fix common issue: '1.1.' → '1.1'
    if re.match(r"^\d+(?:\.\d+)*\.\s", text):
        text = re.sub(r"^(\d+(?:\.\d+)*)(\.)\s+", r"\1 ", text)
    else:
        text = re.sub(r"\s+", " ", text)  # remove weird extra spaces

    # Final regex to parse clean header
    match = re.match(r"^(\d+(?:\.\d+)*)(?:\.)?\s+(.+)$", text)
    if match:
        section_number, title = match.groups()
        return f"{section_number} {title.strip()}"
    return text


def extract_topics(pdf_path: str) -> OrderedDictType[str, str]:
    """
    Extract topic-wise text from a PDF.

    Identifies headers using is_topic_header, cleans them, and aggregates
    subsequent lines into the current topic until the next header.
    Returns an OrderedDict to preserve section order.
    """
    content: OrderedDictType[str, str] = OrderedDict()
    current_topic: str = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                if is_topic_header(line):
                    current_topic = clean_header(line)
                    if current_topic not in content:
                        content[current_topic] = ""
                elif current_topic:
                    # Accumulate text under current topic
                    content[current_topic] += line + "\n"

    return content


__all__ = [
    "is_topic_header",
    "clean_header",
    "extract_topics",
]