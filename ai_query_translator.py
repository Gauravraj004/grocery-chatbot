"""
Deprecated: ai_query_translator.py

This module is no longer used. The project now uses `query_translator.py`
with a Pydantic schema and list-based fields. Keeping this file raises
an explicit error if imported to prevent accidental use.
"""

raise ImportError(
    "ai_query_translator.py is deprecated. Use query_translator.QueryTranslator instead."
)
