import json
import re
from google import genai
import src.config as config

# Initialize the Gemini API client if the key is available
client = None
if config.GEMINI_API_KEY:
    client = genai.Client(api_key=config.GEMINI_API_KEY)
else:
    print("[WARNING] GEMINI_API_KEY is not set. Gemini API calls will fail.")


def suggest_new_company(analyzed_companies: list) -> dict:
    """
    Queries Gemini to suggest a successful B2B/PLG/bootstrapped/micro-SaaS company
    that has not been analyzed yet.
    """
    if not client:
        raise ValueError("GEMINI_API_KEY is not configured.")

    
    # Construct a list of names/websites to exclude
    excluded_names = [item.get("name", "").strip() for item in analyzed_companies]
    excluded_websites = [item.get("website", "").strip() for item in analyzed_companies]
    
    prompt = f"""
You are a startup intelligence analyst and venture capital researcher.
Recommend a single highly successful, profitable, bootstrapped, PLG, or fast-growing SaaS company (focusing on B2B, PLG, and micro-SaaS) that is NOT in this list of already analyzed companies:
Names: {json.dumps(excluded_names)}
Websites: {json.dumps(excluded_websites)}

Return a clean JSON object containing:
{{
  "name": "Company Name",
  "website": "Company Website URL (e.g., https://example.com)",
  "category": "Company Category"
}}

Rules:
- Choose real, operational companies.
- Provide a valid website URL.
- Wrap the JSON in a markdown block: ```json ... ```. Do not include any other text outside the block.
"""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt
    )
    raw_text = response.text.strip()
    
    # Parse the JSON from the markdown block
    match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = raw_text

    try:
        data = json.loads(json_str)
        if "name" in data and "website" in data and "category" in data:
            return data
        else:
            raise KeyError("JSON missing required fields.")
    except Exception as e:
        print(f"[ERROR] Failed to parse LLM suggestion: {e}. Raw text was:\n{raw_text}")
        raise ValueError("Could not get valid company suggestion from Gemini.")

def generate_report(company_info: dict, report_number: int) -> str:
    """
    Asks Gemini to research the company and generate a comprehensive Founder Intelligence Report
    in the exact format specified by the user.
    """
    if not client:
        raise ValueError("GEMINI_API_KEY is not configured.")

    
    name = company_info.get("name")
    website = company_info.get("website")
    category = company_info.get("category")
    
    prompt = f"""
You are an expert SaaS Analyst, Growth Marketer, and Product Strategist.
Research the SaaS company '{name}' (Website: {website}, Category: {category}) using your training data, web search indices, and deep startup intelligence.
Produce a comprehensive report reverse engineering their business, answering the following core objectives:
1. What pain point existed?
2. Why was it painful?
3. How were people solving it before?
4. What did the company build?
5. Why did customers pay?
6. How did the company acquire users?
7. What is the business model?
8. What is the moat?
9. What mistakes were made?
10. Can a smaller version be built today?
11. What lessons can founders steal?

You MUST format the output EXACTLY as shown in the POST FORMAT template below. Use simple Telegram-compatible HTML tags for formatting if helpful, such as:
- <b>text</b> for bold (e.g. section headers or labels)
- <i>text</i> for italics
- <code>text</code> for code blocks
- <a href="url">text</a> for hyperlinks (Note: use double quotes inside href)

POST FORMAT TEMPLATE:
━━━━━━━━━━━━━━━━━━
🚀 <b>SAAS INTELLIGENCE REPORT #{report_number}</b>
━━━━━━━━━━━━━━━━━━

🏢 <b>COMPANY</b>

<b>Name:</b> {name}
<b>Website:</b> <a href="{website}">{website}</a>
<b>Category:</b> {category}
<b>Founded:</b> [Year it was founded, e.g. 2015]

━━━━━━━━━━━━━━━━━━

🎯 <b>CORE PAIN POINT</b>

<b>Problem:</b>
[What specific problem existed? Detailed explanation]

<b>Who Experienced This Problem?</b>
[Bullet list of target customer profiles]

<b>Pain Severity:</b> [X]/10
<b>Urgency:</b> [X]/10
<b>Frequency:</b> [X]/10

<b>Why Was It Painful?</b>
[Detailed explanation of the emotional or business cost of this problem]

━━━━━━━━━━━━━━━━━━

❌ <b>OLD SOLUTION</b>

<b>How People Solved It Before:</b>
* [Method 1]
* [Method 2]
* [Method 3]

<b>Why Existing Solutions Failed:</b>
* [Reason 1]
* [Reason 2]
* [Reason 3]

━━━━━━━━━━━━━━━━━━

✅ <b>THE SAAS SOLUTION</b>

<b>What Did The Company Build?</b>
[Detailed explanation of the product solution]

<b>Main Feature:</b>
[Describe the primary feature that drove adoption]

<b>Supporting Features:</b>
* [Feature 1]
* [Feature 2]
* [Feature 3]

<b>Unique Advantage:</b>
[Explain why this solution was vastly superior]

━━━━━━━━━━━━━━━━━━

💰 <b>WHY CUSTOMERS PAID</b>

* <b>[Benefit #1]</b>: [Detailed explanation]
* <b>[Benefit #2]</b>: [Detailed explanation]
* <b>[Benefit #3]</b>: [Detailed explanation]
* <b>[Benefit #4]</b>: [Detailed explanation]

<b>Main Outcome:</b>
[The ultimate result/ROI the customer achieved]

━━━━━━━━━━━━━━━━━━

👥 <b>CUSTOMER PROFILE</b>

<b>Primary Customer:</b>
[Bullet points of customer segments]

<b>Business Size:</b>
[Bullet points of business sizes, e.g., Solopreneurs, SMBs, Mid-market, Enterprise]

━━━━━━━━━━━━━━━━━━

📈 <b>GROWTH ENGINE</b>

<b>Acquisition Channels:</b>
* [Channel 1, e.g. SEO]
* [Channel 2, e.g. PLG / Viral loop]
* [Channel 3]

<b>Primary Growth Lever:</b>
[Detailed explanation of their most effective distribution mechanism]

<b>Growth Loop:</b>
User
↓
[User Action]
↓
[Exposure/Invitation]
↓
New User

━━━━━━━━━━━━━━━━━━

💵 <b>REVENUE MODEL</b>

<b>Business Model:</b>
[e.g., Freemium, Usage-based, Tiered SaaS Subscription]

<b>Pricing Logic:</b>
[How they set pricing and value metrics, e.g., per-seat, volume of emails]

<b>Why Customers Upgraded:</b>
[Key drivers prompting upgrade from free to paid, or lower tier to higher tier]

━━━━━━━━━━━━━━━━━━

🛡 <b>COMPETITIVE MOAT</b>

<b>Moat Type:</b>
* [Moat type(s) from: Brand, Distribution, Data, Integrations, Community, Network Effects]

<b>Moat Strength:</b> [X]/10

<b>Why It Is Difficult To Copy:</b>
[Detailed explanation]

━━━━━━━━━━━━━━━━━━

⚠ <b>RISKS & MISTAKES</b>

<b>Major Mistakes:</b>
[List of errors they made during their growth journey]

<b>Current Risks:</b>
[List of current threats they face today, e.g., platform risk, copycats, AI disruption]

━━━━━━━━━━━━━━━━━━

🧠 <b>FOUNDER LESSON</b>

<b>Most Important Lesson:</b>
[The key actionable advice/lesson founders can take away from this company]

━━━━━━━━━━━━━━━━━━

🇮🇳 <b>INDIA OPPORTUNITY</b>

<b>Can This Concept Work In India?</b>
[YES / NO]

<b>Target Audience:</b>
[Bullet list of target segments in India]

<b>Market Potential:</b> [X]/10

<b>Reason:</b>
[Detailed explanation of why this model does/doesn't translate to the Indian market]

━━━━━━━━━━━━━━━━━━

🚀 <b>MICRO-SAAS VERSION</b>

<b>How A Solo Founder Could Build A Smaller Version:</b>
[Specific product scope and idea for a solo founder/indie hacker]

<b>MVP Features:</b>
* [Core MVP Feature 1]
* [Core MVP Feature 2]
* [Core MVP Feature 3]

<b>Potential First Customers:</b>
[Bullet points of who to pitch first]

<b>Possible Monthly Pricing:</b>
₹[Recommended price in INR, e.g. ₹999/mo]

━━━━━━━━━━━━━━━━━━

📊 <b>OPPORTUNITY SCORE</b>

<b>Pain Point:</b> [X]/10
<b>Market Size:</b> [X]/10
<b>Monetization:</b> [X]/10
<b>Competition:</b> [X]/10
<b>Execution Difficulty:</b> [X]/10
<b>Overall Opportunity:</b> [X]/10

━━━━━━━━━━━━━━━━━━

🔥 <b>ONE SENTENCE SUMMARY</b>

[Explain the entire business in one sentence.]

━━━━━━━━━━━━━━━━━━

#SaaSIntelligence
#StartupBreakdown
#MicroSaaS
#FounderLessons
"""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt
    )
    return response.text.strip()

def extract_opportunity_score(report_text: str) -> int:
    """
    Parses the report text to find the overall opportunity score.
    Looks for the pattern: <b>Overall Opportunity:</b> [X]/10 or similar.
    Returns the score as an integer out of 10.
    """
    # Regex searches for "Overall Opportunity:" followed by digits
    patterns = [
        r"Overall\s+Opportunity:</b>\s*\[?(\d+)\]?\s*/\s*10",
        r"Overall\s+Opportunity:</b>\s*\*?(\d+)\*?\s*/\s*10",
        r"Overall\s+Opportunity:</b>\s*(\d+)\s*/\s*10",
        r"Overall\s+Opportunity:\s*\[?(\d+)\]?\s*/\s*10",
        r"Overall Opportunity:\s*\*?(\d+)\*?\s*/\s*10",
        r"Overall Opportunity:\s*(\d+)\s*/\s*10"
    ]
    for pattern in patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
                
    # Fallback search for any "Score: X/10" in the opportunity score block
    match = re.search(r"Overall.*?(\d+)\s*/\s*10", report_text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
            
    return 7 # Default fallback score
