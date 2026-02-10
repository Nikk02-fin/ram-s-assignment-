import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI manufacturing concierge.
Your job is to ask concise, practical questions to understand
manufacturing requirements. Avoid technical jargon.
"""

EXTRACTION_PROMPT = """
Extract manufacturing requirements from the conversation below.
Return ONLY valid JSON with these exact fields:

{
  "product_type": "string (broad category: electronics, consumer_goods, industrial, apparel, jeans, fashion, etc.)",
  "product_description": "string (specific product the user wants to make, e.g., jackets, kitchen organizers, phone cases, denim jeans)",
  "materials": ["array of strings (e.g., plastic, metal, abs, denim, cotton)"],
  "moq": number (minimum order quantity),
  "geography": "string or null (e.g., China, Vietnam, Europe, Bangladesh, India)",
  "certifications": ["array of strings (e.g., ISO9001, BSCI, CE, GOTS, WRAP)"],
  "budget_tier": "string or null (low, medium, or high)"
}

Important mapping rules:
- product_type: Map to broad category that matches factory database: "electronics", "consumer_goods", "industrial", "apparel", "jeans", "fashion", "jackets"
  Examples: "jackets" -> "jackets", "kitchen organizer" -> "consumer_goods", "phone case" -> "electronics", "denim jeans" -> "jeans"
- product_description: Extract the EXACT specific product the user mentioned (e.g., "winter jackets", "plastic kitchen organizers", "wireless earbuds")
  This should be what the user actually wants to manufacture, not the category
- materials: Extract all mentioned materials as lowercase strings
- moq: Extract the quantity number
- geography: Map to specific regions from the conversation
- certifications: Extract any mentioned certifications or use empty array []
- budget_tier: Map cost mentions to "low", "medium", or "high", or use null if not mentioned

Return ONLY the JSON, no explanations.
"""

def chat(messages):
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

def extract_requirements(conversation_text):
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": conversation_text}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content
