import os
import google.generativeai as genai
from typing import Dict

# Load API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize model
MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(model_name=MODEL_NAME)


# -------- System Prompt --------
SYSTEM_PROMPT = """
You are an expert professional email writer.

Guidelines:
- Generate clear, polite, and context-aware emails.
- Handle Indian business, personal, and cultural contexts naturally.
- Support Hinglish (Hindi + English mixed) gracefully when language is Hinglish.
- Keep tone aligned with Indian communication styles (respectful, warm, concise).
- Do NOT use slang unless explicitly requested.
- Output must always be structured and professional.
"""


# -------- Email Generator --------
def generate_email(
    prompt: str,
    tone: str = "professional",
    language: str = "English"
) -> Dict[str, str]:
    """
    Generate a structured email with subject and body
    """

    user_prompt = f"""
    Language: {language}
    Tone: {tone}

    Task:
    Write an email based on the following input:

    "{prompt}"

    Return response strictly in this format:
    Subject: <email subject>
    Body:
    <email body>
    """

    response = model.generate_content(
        [
            {"role": "system", "parts": [SYSTEM_PROMPT]},
            {"role": "user", "parts": [user_prompt]},
        ]
    )

    text = response.text.strip()

    # Basic parsing (safe & predictable)
    subject = ""
    body = ""

    if "Subject:" in text and "Body:" in text:
        subject = text.split("Subject:")[1].split("Body:")[0].strip()
        body = text.split("Body:")[1].strip()
    else:
        # Fallback if model formatting deviates
        subject = "Regarding your request"
        body = text

    return {
        "subject": subject,
        "body": body
    }


# -------- Email Summarizer --------
def summarize_email(email_content: str) -> str:
    """
    Generate a 2-line summary of the email
    """

    summary_prompt = f"""
    Summarize the following email in exactly 2 concise lines.
    Maintain clarity and Indian context if present.

    Email Content:
    {email_content}
    """

    response = model.generate_content(
        [
            {"role": "system", "parts": [SYSTEM_PROMPT]},
            {"role": "user", "parts": [summary_prompt]},
        ]
    )

    return response.text.strip()
