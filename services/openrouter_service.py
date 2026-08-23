"""
OpenRouter LLM Client Service
Provides intelligent LLM completion for Product Enrichment, Descriptions,
Technical Summaries, Q&A, Attribute Extraction, and Compatibility Recommendations.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")

class OpenRouterLLM:
    """
    OpenRouter API Wrapper for Industrial Product Intelligence.
    """

    @classmethod
    def call_llm(cls, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.2) -> Optional[str]:
        api_key = os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
        if not api_key:
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Rutuja-131005/AI-Powered-Product-Intelligence-for-Industrial-Commerce",
            "X-Title": "ProdIntellix Product Intelligence"
        }

        payload = {
            "model": model or DEFAULT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000
        }

        try:
            response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"OpenRouter API error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"OpenRouter request failed: {e}")
        return None

    @classmethod
    def generate_product_description(cls, brand: str, part_num: str, part_desc: str, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generates commerce descriptions, technical summary, and feature bullets via OpenRouter."""
        prompt = f"""
        Act as an Industrial Catalog Expert. Given this product data:
        - Brand: {brand}
        - Part Number: {part_num}
        - Description: {part_desc}
        - Verified Specs: {json.dumps(specs)}

        Provide a JSON object with:
        1. "marketing_desc": A 2-3 sentence commercial product overview.
        2. "technical_summary": A concise engineering summary highlighting key specifications.
        3. "features": A list of 4-6 concise technical feature bullet points.
        4. "recommendations": A 1-2 sentence recommendation on ideal industrial use-cases and accessories.

        Output ONLY valid JSON.
        """
        response_text = cls.call_llm([
            {"role": "system", "content": "You output strictly valid JSON format with no markdown wrappers."},
            {"role": "user", "content": prompt}
        ])

        if response_text:
            try:
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)
            except Exception:
                pass

        # Fallback heuristic summary
        return {
            "marketing_desc": f"The {brand} {part_num} is an industrial-grade solution designed for high-performance operations.",
            "technical_summary": f"Commercial hardware component ({part_num}) manufactured by {brand}. Engineered for professional applications.",
            "features": [
                f"Manufactured by {brand}",
                f"Part Number: {part_num}",
                "Industrial durability standards",
                "Optimized for high-cycle commercial use"
            ],
            "recommendations": f"Recommended for maintenance, manufacturing, and industrial trade applications matching {brand} specifications."
        }

    @classmethod
    def answer_qa(cls, query: str, context: str) -> str:
        """Answers technical Q&A against retrieved document/catalog context."""
        prompt = f"""You are ProdIntellix AI, an industrial product intelligence assistant.
        Answer the following question STRICTLY based on the provided technical catalog context.
        If the information is not present in the context, state that clearly and provide general industrial guidance.

        Technical Context:
        {context}

        Question: {query}
        Answer:"""

        res = cls.call_llm([
            {"role": "system", "content": "You are a professional industrial commerce AI assistant."},
            {"role": "user", "content": prompt}
        ])
        return res or "No direct answer could be generated from available context."
