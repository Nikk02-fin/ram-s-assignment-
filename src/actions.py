import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_rfq(factory, req):
    # Use product_description if available, otherwise fall back to product_type
    product_name = req.product_description if req.product_description else req.product_type
    
    prompt = f"""
Draft a professional Request for Quote (RFQ) email to the following manufacturing factory.

Factory Details:
- Name: {factory['name']}
- Location: {factory['geography']}
- Certifications: {', '.join(factory['certifications'])}

Our Requirements:
- Product: {product_name}
- Materials: {', '.join(req.materials) if req.materials else 'To be discussed'}
- Target MOQ: {req.moq} units
- Geographic Preference: {req.geography or 'Flexible'}
- Required Certifications: {', '.join(req.certifications) if req.certifications else 'To be discussed'}
- Budget Tier: {req.budget_tier or 'To be discussed'}

The email should:
1. Be professional and concise
2. Introduce our company/project briefly
3. Clearly state our specific product requirements (mention "{product_name}" specifically)
4. Request: pricing per unit, lead time, MOQ confirmation, sample availability, and next steps
5. Express interest in establishing a partnership
6. Include a polite closing

Format as a ready-to-send email with subject line.
"""

    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content
