import streamlit as st
from llm import chat, extract_requirements
from factories import load_factories
from actions import generate_rfq
from model.requirements import ManufacturingRequirements
import json
import re

st.set_page_config(page_title="AI Manufacturing Concierge", layout="wide")

# Custom CSS for ChatGPT-style interface
st.markdown("""
    <style>
    /* Dark background for the app */
    .stApp {
        background-color: #1a1a1a;
    }
    
    /* Main title styling */
    h1 {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    p {
        text-align: left;
        color: #cccccc;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }
    
    /* Input box styling - dark theme */
    .stChatInputContainer {
        border-top: 1px solid #3a3a3a;
        padding-top: 1.5rem;
        background-color: #1a1a1a;
    }
    
    .stChatInputContainer textarea {
        border-radius: 12px;
        border: 2px solid #3a3a3a;
        padding: 12px 16px;
        font-size: 1rem;
        background-color: #2a2a2a;
        color: white;
    }
    
    .stChatInputContainer textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2a2a2a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4a4a4a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a5a5a;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <h1>🏭 ManuGPT</h1>
    <p style='text-align: center; color: #666; font-size: 1.1rem; margin-top: -1rem; margin-bottom: 2rem;'>
        Your AI Manufacturing Concierge
    </p>
    """,
    unsafe_allow_html=True
)

# Load factories data to include in AI context
factories_data = load_factories()

# Enhanced system prompt with factories data
ENHANCED_SYSTEM_PROMPT = f"""
You are an AI manufacturing concierge assistant. Your goal is to help users find the right manufacturing factory from our database.

Available Factories in our Database:
{json.dumps(factories_data, indent=2)}

Required information to collect:
1. product_type (e.g., electronics, consumer_goods, industrial)
2. materials (e.g., plastic, metal, abs)
3. moq (minimum order quantity as a number)
4. geography (preferred location, e.g., China, Vietnam, Europe)
5. certifications (e.g., ISO9001, BSCI, CE)
6. budget_tier (low, medium, or high)

Instructions:
- Ask concise, practical questions to gather requirements
- Be friendly and conversational
- Once you have enough information (at least product_type, materials, and moq), analyze ALL factories in the database above
- IMPORTANT GEOGRAPHY RULE: If user specifies a geography preference (e.g., "Asia", "China", "Vietnam", "Europe", "USA"), you MUST prioritize factories in that region
  * For "Asia" preference: ONLY recommend factories in China, Vietnam, Bangladesh, India, or other Asian countries
  * For "Europe" preference: ONLY recommend factories in Europe
  * For "USA" or "America" preference: ONLY recommend factories in USA
  * Geographic match is CRITICAL - do NOT recommend factories outside the preferred region
- Recommend EXACTLY the TOP 3 most suitable factories, ranked by best fit
- Scoring criteria (in order of importance):
  1. Geographic preference match (HIGHEST PRIORITY - must be in the requested region)
  2. Product type match (very high priority)
  3. Material compatibility
  4. MOQ capability (can they handle the requested quantity?)
  5. Certification requirements
  6. Budget tier alignment
- For EACH of the 3 recommended factories, provide:
  * Clear ranking (#1, #2, #3)
  * Factory name and location
  * Match score or "fit" explanation
  * Specific strengths (why this factory is good for their needs)
  * Trade-offs or limitations (e.g., higher MOQ, different location, cost differences)
  * Key details: MOQ minimum, certifications, cost tier
- Compare the 3 factories to help user make informed decision
- Use clear formatting with numbered recommendations
- AFTER presenting all 3 recommendations, ALWAYS ask: "Would you like me to generate a Request for Quote (RFQ) email for any of these factories?"
- When user asks for RFQ, respond with: "GENERATE_RFQ: [Factory Name]" (use exact factory name from database)
- If fewer than 3 factories in the preferred geography match, recommend all matches in that region and explain why there are fewer than 3
- Avoid technical jargon
"""

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": ENHANCED_SYSTEM_PROMPT}]
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm here to help you find the perfect manufacturing partner. Tell me about your product - what are you looking to manufacture?"
    })

if "requirements" not in st.session_state:
    st.session_state.requirements = None

# Display chat history with custom styling for left/right alignment
for message in st.session_state.messages:
    if message["role"] != "system":
        # Don't show GENERATE_RFQ trigger messages
        if not message["content"].startswith("GENERATE_RFQ:"):
            if message["role"] == "user":
                # User message on the right using columns
                col1, col2 = st.columns([1, 4])
                with col2:
                    st.markdown(f"""
                        <div style="padding: 1rem 1.5rem; 
                                    margin: 0.5rem 0;
                                    margin-left: auto;
                                    width: fit-content;
                                    max-width: 100%;
                                    float: right;
                                    text-align: right;">
                            <div style="color: white;">
                                {message["content"]}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                # Assistant message on the left using columns
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                        <div style="padding: 1rem 1.5rem; 
                                    margin: 0.5rem 0;
                                    width: fit-content;
                                    max-width: 100%;">
                            <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                                <div style="font-size: 1.5rem;">🤖</div>
                                <div style="flex: 1; color: white;">
                                    {message["content"]}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately (right-aligned)
    col1, col2 = st.columns([1, 4])
    with col2:
        st.markdown(f"""
            <div style="padding: 1rem 1.5rem; 
                        margin: 0.5rem 0;
                        margin-left: auto;
                        width: fit-content;
                        max-width: 100%;
                        float: right;
                        text-align: right;">
                <div style="color: white;">
                    {prompt}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Get AI response
    with st.spinner("🤖 Analyzing..."):
        reply = chat(st.session_state.messages)
        
        # Check if AI wants to generate RFQ
        if reply.startswith("GENERATE_RFQ:"):
            # Extract factory name from the response
            factory_name_match = re.search(r"GENERATE_RFQ:\s*(.+)", reply)
            if factory_name_match:
                factory_name = factory_name_match.group(1).strip()
                
                # Find the factory in the database
                factory = None
                for f in factories_data:
                    if f["name"].lower() in factory_name.lower() or factory_name.lower() in f["name"].lower():
                        factory = f
                        break
                
                if factory:
                    # Extract requirements from conversation if not already extracted
                    if st.session_state.requirements is None:
                        conversation_text = "\n".join(
                            [m["content"] for m in st.session_state.messages if m["role"] != "system"]
                        )
                        try:
                            raw = extract_requirements(conversation_text)
                            req = ManufacturingRequirements(**json.loads(raw))
                            st.session_state.requirements = req
                        except Exception as e:
                            st.error(f"Error extracting requirements: {e}")
                            req = None
                    else:
                        req = st.session_state.requirements
                    
                    if req:
                        # Generate RFQ email
                        rfq_email = generate_rfq(factory, req)
                        
                        # Create a nice formatted response
                        rfq_response = f"📧 **Request for Quote (RFQ) Email Generated**\n\n"
                        rfq_response += f"**To:** {factory['name']}\n\n"
                        rfq_response += "---\n\n"
                        rfq_response += rfq_email
                        rfq_response += "\n\n---\n\n"
                        rfq_response += "Feel free to copy this email and send it to the manufacturer!"
                        
                        reply = rfq_response
                else:
                    reply = f"I couldn't find the factory '{factory_name}' in our database. Please specify one of the recommended factories."
            else:
                reply = "I had trouble identifying which factory you want the RFQ for. Could you please specify the factory name?"
    
    # Display assistant response (left-aligned)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
            <div style="padding: 1rem 1.5rem; 
                        margin: 0.5rem 0;
                        width: fit-content;
                        max-width: 100%;">
                <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                    <div style="font-size: 1.5rem;">🤖</div>
                    <div style="flex: 1; color: white;">
                        {reply}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
