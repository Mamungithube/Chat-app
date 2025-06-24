import os
import re
import time
import random
import logging
from functools import lru_cache
from openai import OpenAI, APIError
from typing import Dict, List, Tuple, Optional

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- API Key Validation ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable")
client = OpenAI(api_key=OPENAI_API_KEY)

MAX_HISTORY_LENGTH = 20
MAX_RETRIES = 3

# --- System Prompt ---
SYSTEM_PROMPT = """
You are Bondly, an emotionally intelligent and compassionate financial coach designed to support {relationship_desc} in building financial confidence, managing money, and achieving their goals together or independently.

Your core responsibilities include:

1. Emotional Support & Communication Guidance  
- Help users navigate their feelings about money with empathy and validation.  
- Reframe stress or conflict gently, and offer conversation starters for financial discussions, especially for couples.  
- Adjust your tone dynamically based on user mood and tone preference: {tone_preference}. Use gentle validation for stress, and motivation for readiness.

2. Financial Coaching & Planning  
- Provide clear, smart financial suggestions on budgets, saving, investing, and goal-setting.  
- Tailor advice based on relationship status (single or partnered), income, and life milestones.  
- Make financial concepts approachable, emotionally aligned, and manageable.

3. Portfolio and Tax Education Guidance  
- Educate users on investing based on risk tolerance (conservative, moderate, aggressive) and financial goal timelines (short, medium, long term).  
- Suggest general diversified portfolio ideas in simple language.  
- Explain individual investment classes (stocks, ETFs, bonds, crypto, real estate) focusing on risks and general nature without specific buy/sell recommendations.  
- Provide general tax information with clear disclaimers that you do not give tax advice and recommend consulting tax professionals.

4. Broad Asset Allocation and Historical Performance  
- Suggest broad asset allocation frameworks based on risk profile and goals.  
- Educate users on historical investment trends up to April 2023, emphasizing past performance does not guarantee future results.

5. Emotional Adaptiveness and Trust Building  
- Track and celebrate user wins, milestones, and consistency streaks to build motivation.  
- Use micro-consent by asking users if they want suggestions before providing advice, tracking consent requests separately per topic.  
- In conflict or emotional conversations, acknowledge the difficulty, validate feelings, and offer gentle reframing or next steps. Use empathetic conversation starters from your conflict scripts.  
- Use natural, warm, human-like language, speaking like a trusted coach or friend.

6. Name Personalization  
- When the user's first name is known, use it naturally in greetings, encouragement, and celebrations.

Your tone and language guidelines:  
- Warm, supportive, inclusive, non-judgmental, and clear.  
- Use inclusive pronouns like “we,” “you both,” and “together” when addressing couples.  
- Avoid jargon unless the user asks for more technical detail.  
- Keep responses concise (under 100 words) unless the user requests more depth.  
- End every interaction with a validating, emotionally aware remark and one clear, practical next step.

Compliance and legal disclaimers:  
- Bondly provides general educational information, not personalized financial, investment, or tax advice.  
- Always remind users to consult licensed financial advisors or tax professionals for personalized advice.  
- Bondly offers emotional intelligence tools but is not a therapist or counselor; recommend licensed mental health professionals for emotional or relationship counseling.

User Context for personalization:  
- First name: {first_name}  
- Partner names: {partner_names}  
- Relationship status: {relationship_status}  
- Mood: {mood}  
- Tone preference: {tone_preference}  
- Money personality: {money_personality}  
- Active financial goals: {goal_summaries}  
- Risk tolerance: {risk_profile}  
- Investment timeline: {investment_timeline}  
- Conflict patterns: {conflict_patterns}  

You are Bondly — the trusted, emotionally intelligent financial coach who helps {relationship_desc} build trust, confidence, and progress with their money — together or independently.
"""

CONFLICT_SCRIPTS = [
    "I understand financial discussions can be challenging. Remember, it's okay to feel overwhelmed. I'm here to help you navigate this gently.",
    "Money conversations with a partner can bring up strong emotions. Let's approach this with patience and understanding.",
    "Conflicts happen, but talking about finances openly is a strong step forward. I can suggest some ways to ease the conversation if you'd like.",
    "It's normal to feel stressed about money matters. Let's take this one step at a time together."
]

# --- Helper: Format multiple goals summary ---
def format_goals_summary(goals: List[Dict]) -> str:
    """Formats a summary of financial goals."""
    if not goals:
        return "No active financial goals currently."
    summaries = [f"{idx}. {goal['type']} - Target: ${goal['target_amount']} by {goal['target_date']} (Saved: ${goal.get('saved_amount', 0)})" for idx, goal in enumerate(goals, 1)]
    return " | ".join(summaries)

# --- Detect user mood with conflict awareness ---
def detect_mood(user_input: str, user_data: Dict) -> str:
    """Detects user mood based on input and conflict patterns."""
    stressed_keywords = ['stressed', 'overwhelmed', 'anxious', 'upset', 'frustrated', 'tired', 'confused']
    motivated_keywords = ['ready', 'motivated', 'excited', 'happy', 'good', 'great']
    text = user_input.lower()
    conflict_terms = ['argue', 'fight', 'disagree', 'conflict', 'stress', 'frustrate']
    conflict_detected = any(term in text for term in conflict_terms) or bool(user_data.get("conflict_patterns"))
    if any(word in text for word in stressed_keywords) or conflict_detected:
        return 'gentle, validating, and supportive tone'
    elif any(word in text for word in motivated_keywords):
        return 'motivating, clear, and growth-oriented tone'
    return 'friendly and calm tone'

# --- Detect user intent with more granularity ---
def detect_intent(user_input: str) -> str:
    """Detects user intent based on input keywords."""
    text = user_input.lower()
    if re.search(r'\b(save|goal|plan|budget|track)\b', text):
        return "goal_setting"
    if re.search(r'\b(spend|expenses|budget|review)\b', text):
        return "budget_review"
    if re.search(r'\b(debt|credit card|pay off|loans)\b', text):
        return "debt_paydown"
    if re.search(r'\b(feel|upset|stressed|worried|anxious|frustrated)\b', text):
        return "emotional_encouragement"
    if re.search(r'\b(invest|portfolio|stocks|bonds|crypto|real estate|asset)\b', text):
        return "investment_guidance"
    return "general"

# --- Build system prompt with tone and multi-goal summary, with caching ---
@lru_cache(maxsize=1000)
def build_system_prompt(first_name: str, partner_names: str, relationship_status: str, tone_preference: str, goals_tuple: tuple, mood: str, money_personality: str, risk_profile: str, investment_timeline: str, conflict_patterns: str) -> str:
    """Builds a personalized system prompt with caching."""
    goals = [{"type": g[0], "target_amount": g[1], "target_date": g[2], "saved_amount": g[3]} for g in goals_tuple]
    relationship_desc = "couples" if relationship_status == "partnered" else "individuals"
    goals_summary = format_goals_summary(goals)
    prompt = SYSTEM_PROMPT.format(
        relationship_desc=relationship_desc,
        first_name=first_name,
        partner_names=partner_names,
        relationship_status=relationship_status,
        mood=mood,
        tone_preference=tone_preference,
        money_personality=money_personality,
        goal_summaries=goals_summary,
        risk_profile=risk_profile,
        investment_timeline=investment_timeline,
        conflict_patterns=conflict_patterns
    )
    logger.info("Built system prompt for user: %s", first_name)
    return prompt

# --- Micro-consent handling ---
def check_micro_consent(user_input: str, user_data: Dict, intent: str) -> Tuple[bool, Optional[str]]:
    """Checks for user consent before providing advice on sensitive topics."""
    if intent not in user_data.get("granted_consents", {}):
        user_data.setdefault("granted_consents", {})[intent] = False
    if not user_data["granted_consents"][intent]:
        if re.search(r'\b(yes|sure|please|ok|okay|go ahead|yep)\b', user_input.lower()):
            user_data["granted_consents"][intent] = True
            return True, None
        return False, f"Before I provide advice on {intent.replace('_', ' ')}, would you like me to proceed with suggestions?"
    return True, None

# --- Conflict empathy message generator ---
def get_conflict_empathy() -> str:
    """Returns a random empathy message for conflict situations."""
    return random.choice(CONFLICT_SCRIPTS)

# --- Pronoun replacement with regex for accuracy ---
def adjust_pronouns(text: str, relationship_status: str) -> str:
    """Adjusts pronouns for couples or individuals."""
    if not text or relationship_status != "partnered":
        return text
    replacements = {
        r'\b(you)\b': 'you both',
        r'\b(your)\b': 'your shared',
        r'\b(yourselves)\b': 'yourselves together'
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

# --- Milestone celebration (only once) ---
def check_milestones(user_data: Dict) -> Optional[str]:
    """Checks and celebrates financial milestones."""
    total_saved = sum(goal.get("saved_amount", 0) for goal in user_data.get("financial_goals", []))
    if total_saved > 50000 and not user_data.get("milestone_celebrated", False):
        user_data["milestone_celebrated"] = True
        return f"Congratulations! You've saved over ${total_saved} towards your goals. Keep up the great work!"
    if user_data.get("budget_diff", 0) > 0:
        return "Nice job on staying under budget this month!"
    return None

# --- Legal disclaimer based on intent ---
def get_legal_disclaimer(intent: str) -> Optional[str]:
    """Returns a legal disclaimer for specific intents."""
    if intent in ['investment_guidance', 'debt_paydown']:
        return "Disclaimer: I provide general educational information only. Please consult licensed financial or tax professionals for personalized advice."
    return None

# --- Prune conversation history to last MAX_HISTORY_LENGTH messages ---
def prune_conversation_history(history: List[Dict]) -> List[Dict]:
    """Limits conversation history to MAX_HISTORY_LENGTH."""
    return history[-MAX_HISTORY_LENGTH:] if len(history) > MAX_HISTORY_LENGTH else history

# --- Input sanitization ---
def sanitize_input(user_input: str) -> str:
    """Sanitizes user input to remove dangerous characters."""
    return re.sub(r'[<>;]', '', user_input)

# --- OpenAI Chat Completion call with retries and streaming, with response caching ---
@lru_cache(maxsize=1000)
def call_openai_chat(messages: tuple) -> str:
    """Calls OpenAI API with retries and caching."""
    messages_list = [{"role": msg[0], "content": msg[1]} for msg in messages]
    logger.info("Calling OpenAI API with %d messages", len(messages_list))
    retries = 0
    response_text = ""
    while retries < MAX_RETRIES:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_list,
                stream=True
            )
            for chunk in response:
                chunk_message = getattr(chunk.choices[0].delta, "content", "") or ""
                response_text += chunk_message
            logger.info("OpenAI API call successful")
            return response_text or "Sorry, I couldn't generate a response. Please try again."
        except APIError as e:
            retries += 1
            logger.error(f"OpenAI API error (retry {retries}/{MAX_RETRIES}): {str(e)}")
            time.sleep(2 * (2 ** retries))  # Exponential backoff
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return "Sorry, something went wrong. Please try again later."
    return "Sorry, I'm having trouble processing your request right now. Please try again later."

# --- Main Bondly response function ---
def get_bondly_response(user_input: str, user_data: Dict, conversation_history: List[Dict], is_audio: bool = False) -> Tuple[str, List[Dict]]:
    """
    Processes user input and returns Bondly's response with updated conversation history.

    Args:
        user_input (str): User's input message.
        user_data (Dict): User context (first_name, relationship_status, etc.).
        conversation_history (List[Dict]): Conversation history.
        is_audio (bool): Whether input is from audio transcription.

    Returns:
        Tuple[str, List[Dict]]: AI response and updated conversation history.
    """
    user_input = sanitize_input(user_input)
    messages = prune_conversation_history(conversation_history)
    intent = detect_intent(user_input)
    mood = detect_mood(user_input, user_data)
    user_data["mood"] = mood
    
    if not messages or messages[0]["role"] != "system":
        goals_tuple = tuple((g["type"], g["target_amount"], g["target_date"], g.get("saved_amount", 0)) for g in user_data.get("financial_goals", []))
        system_prompt = build_system_prompt(
            user_data.get("first_name", ""),
            user_data.get("partner_names", ""),
            user_data.get("relationship_status", "single"),
            user_data.get("tone_preference", "warm & encouraging"),
            goals_tuple,
            mood,
            user_data.get("money_personality", ""),
            user_data.get("risk_profile", "moderate"),
            user_data.get("investment_timeline", "medium-term"),
            user_data.get("conflict_patterns", "none")
        )
        messages.insert(0, {"role": "system", "content": system_prompt})

    consent_ok, consent_response = check_micro_consent(user_input, user_data, intent)
    if not consent_ok:
        messages.append({"role": "assistant", "content": consent_response})
        return consent_response, messages

    conflict_terms = ['argue', 'fight', 'disagree', 'conflict', 'stress', 'frustrate']
    empathy_text = get_conflict_empathy() + "\n\n" if any(term in user_input.lower() for term in conflict_terms) else ""
    audio_ack = "(Received as a transcribed voice message.)\n\n" if is_audio else ""

    messages.append({"role": "user", "content": user_input})
    response_text = audio_ack + empathy_text + call_openai_chat(tuple((msg["role"], msg["content"]) for msg in messages[-3:]))
    response_text = adjust_pronouns(response_text, user_data.get("relationship_status", "single"))

    milestone_msg = check_milestones(user_data)
    if milestone_msg:
        response_text += "\n\n" + milestone_msg
    legal_note = get_legal_disclaimer(intent)
    if legal_note:
        response_text += "\n\n" + legal_note

    messages.append({"role": "assistant", "content": response_text})
    messages = prune_conversation_history(messages)
    return response_text, messages