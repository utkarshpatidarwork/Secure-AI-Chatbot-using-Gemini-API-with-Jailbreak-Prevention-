import google.generativeai as genai
import re
import datetime

# -------------------------------
# 1. Configure Gemini
# -------------------------------
genai.configure(api_key="API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------
# 2. Jailbreak / Safety Patterns
# -------------------------------
JAILBREAK_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"system\s*prompt",
    r"act\s+as",
    r"jailbreak",
    r"developer\s+mode",
    r"bypass",
    r"roleplay",
    r"secret\s+rules",
]

UNSAFE_OUTPUTS = [
    "how to make a bomb",
    "illegal",
    "harmful",
    "violence",
    "terrorism",
    "child abuse",
    "drug recipe",
]

LOG_FILE = "jailbreak_log.txt"

# -------------------------------
# 3. Helper Functions
# -------------------------------
def log_attempt(stage: str, text: str):
    """Log blocked attempts into file"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] BLOCKED at {stage}: {text}\n")

def is_jailbreak_attempt(prompt: str) -> bool:
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            log_attempt("INPUT (Regex)", prompt)
            return True
    return False

def is_unsafe_output(text: str) -> bool:
    for word in UNSAFE_OUTPUTS:
        if word.lower() in text.lower():
            log_attempt("OUTPUT (Keyword)", text)
            return True
    return False

def ai_moderation_check(text: str, stage: str) -> bool:
    """Use Gemini itself to check for unsafe content"""
    moderation_prompt = f"""
    You are a moderation system. Respond only with 'SAFE' or 'UNSAFE'.
    Text: {text}
    """
    response = model.generate_content(moderation_prompt)
    decision = response.text.strip().upper()
    if decision == "UNSAFE":
        log_attempt(f"{stage} (AI)", text)
        return True
    return False

# -------------------------------
# 4. Chat Function
# -------------------------------
def chat_with_gemini(prompt: str) -> str:
    # Input filtering
    if is_jailbreak_attempt(prompt) or ai_moderation_check(prompt, "INPUT"):
        return "⚠️ Sorry, I cannot process this request."

    # Generate response
    response = model.generate_content(prompt)
    reply = response.text.strip()

    # Output filtering
    if is_unsafe_output(reply) or ai_moderation_check(reply, "OUTPUT"):
        return "⚠️ This response was blocked for safety reasons."

    return reply

# -------------------------------
# 5. Main Chat Loop
# -------------------------------
if __name__ == "__main__":
    print("Secure Gemini Chatbot is running. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Goodbye 👋")
            break

        response = chat_with_gemini(user_input)
        print("Chatbot:", response)

