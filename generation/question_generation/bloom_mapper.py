
# src/generation/bloom_mapper.py
# This module maps the topic content to a chunk size based on the Bloom's taxonomy level and
import tiktoken
from .bloom_config import BLOOM_CONFIG
def get_chunk(topic_content, bloom_level, marks):
    conf = BLOOM_CONFIG[bloom_level]  # Keep key case-sensitive

    chunk_size = conf["chunk_size"]

    if marks not in conf["marks"]:
        raise ValueError(f"Marks {marks} not allowed for level {bloom_level}")

    if chunk_size == "ALL":
        return topic_content

    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(topic_content)

    adjusted_size = int(chunk_size * marks / max(conf["marks"]))
    return encoder.decode(tokens[:adjusted_size])