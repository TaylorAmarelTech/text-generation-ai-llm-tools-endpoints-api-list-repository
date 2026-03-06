"""Structured data extraction agent.

Uses LLMs to extract structured data from unstructured text:
- Named entities (people, places, organizations)
- Key-value pairs
- Tables from prose
- Custom schemas
"""
from __future__ import annotations

import json

from .base import BaseAgent, AgentConfig


EXTRACTOR_SYSTEM_PROMPT = """You are a precise data extraction assistant.
Extract structured information from the given text.
Always respond with valid JSON matching the requested schema.
Only include information explicitly stated in the text.
Use null for fields where information is not available."""


class DataExtractorAgent(BaseAgent):
    """Agent for extracting structured data from unstructured text.

    Usage:
        agent = DataExtractorAgent("groq")

        # Extract entities
        entities = agent.extract_entities("Elon Musk visited SpaceX in Texas.")

        # Extract with custom schema
        data = agent.extract(text, {
            "product_name": "string",
            "price": "number",
            "features": ["string"],
        })
    """

    def __init__(self, config: AgentConfig | str = "groq"):
        super().__init__(config)
        self.config.system_prompt = EXTRACTOR_SYSTEM_PROMPT
        self.config.temperature = 0.1  # Very deterministic for extraction

    def extract(self, text: str, schema: dict) -> dict:
        """Extract data matching a custom schema.

        Args:
            text: The source text
            schema: Dict describing expected fields and types.
                    Example: {"name": "string", "age": "number", "tags": ["string"]}
        """
        schema_desc = json.dumps(schema, indent=2)
        self.reset()
        response = self.chat(
            f"Extract data from this text matching the given JSON schema.\n\n"
            f"Schema:\n```json\n{schema_desc}\n```\n\n"
            f"Text:\n{text}\n\n"
            f"Respond with ONLY valid JSON matching the schema."
        )
        # Try to parse JSON from the response
        try:
            # Handle markdown code blocks
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                clean = clean.rsplit("```", 1)[0]
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"raw_response": response, "parse_error": True}

    def extract_entities(self, text: str) -> dict:
        """Extract named entities (people, organizations, locations, dates)."""
        return self.extract(text, {
            "people": ["string"],
            "organizations": ["string"],
            "locations": ["string"],
            "dates": ["string"],
            "monetary_values": ["string"],
        })

    def extract_key_values(self, text: str) -> dict:
        """Extract key-value pairs from text."""
        self.reset()
        response = self.chat(
            f"Extract all key-value pairs from this text as a flat JSON object. "
            f"Use snake_case keys.\n\nText:\n{text}\n\n"
            f"Respond with ONLY valid JSON."
        )
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                clean = clean.rsplit("```", 1)[0]
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"raw_response": response, "parse_error": True}

    def extract_table(self, text: str, columns: list[str] | None = None) -> list[dict]:
        """Extract tabular data from prose text.

        Args:
            text: Source text containing table-like data
            columns: Optional column names. If None, agent infers them.
        """
        col_hint = f"Columns: {', '.join(columns)}" if columns else "Infer appropriate column names."
        self.reset()
        response = self.chat(
            f"Extract tabular data from this text as a JSON array of objects.\n"
            f"{col_hint}\n\nText:\n{text}\n\n"
            f"Respond with ONLY a valid JSON array."
        )
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                clean = clean.rsplit("```", 1)[0]
            result = json.loads(clean)
            return result if isinstance(result, list) else [result]
        except json.JSONDecodeError:
            return [{"raw_response": response, "parse_error": True}]

    def classify(self, text: str, categories: list[str]) -> dict:
        """Classify text into one or more categories.

        Args:
            text: Text to classify
            categories: List of possible categories
        """
        return self.extract(text, {
            "primary_category": "string (one of: " + ", ".join(categories) + ")",
            "confidence": "number (0-1)",
            "reasoning": "string",
        })
