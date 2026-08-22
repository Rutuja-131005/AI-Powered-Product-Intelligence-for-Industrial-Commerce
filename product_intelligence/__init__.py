"""
AI-Powered Product Intelligence for Industrial Commerce
Extension module for Document RAG System
"""

from .schema import EXPECTED_OUTPUT_COLUMNS, NUM_OUTPUT_COLUMNS
from .pipeline import ProductIntelligencePipeline, get_pipeline_instance

__all__ = [
    "EXPECTED_OUTPUT_COLUMNS",
    "NUM_OUTPUT_COLUMNS",
    "ProductIntelligencePipeline",
    "get_pipeline_instance",
]
