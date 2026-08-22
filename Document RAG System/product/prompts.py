"""
LLM Prompt Templates and JSON Schemas for Product Intelligence
"""

STRUCTURED_EXTRACTION_PROMPT = """
You are an expert industrial catalog engineer. Extract structured technical specifications
from the provided product descriptor and document context.

Return a valid JSON object matching the schema:
{
  "Product_Type": string,
  "Primary_Category": string,
  "Voltage_Rating": string,
  "Current_Rating": string,
  "Mounting_Type": string,
  "Certifications": string,
  "Operating_Temperature_Min": string,
  "Operating_Temperature_Max": string,
  "Attributes": [
     {"name": string, "value": string, "uom": string}
  ]
}

If a technical specification is not supported by evidence, leave its value null. Do not hallucinate.
"""
