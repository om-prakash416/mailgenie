from fastapi import FastAPI
from dotenv import load_dotenv
from app.db.database import connect_to_mongo, close_mongo_connection
from app.routers import whatsapp
from fastapi import FastAPI, Request
from fastapi.responses import Response

from twilio.twiml.messaging_response import MessagingResponse

from app.db.database import connect_to_mongo, close_mongo_connection, get_database
from app.models.user import UserCreate
from app.services.ai_service import generate_email
from app.services.email_service import create_draft


load_dotenv()

app = FastAPI(title="MailGenie")
app.include_router(whatsapp.router)

@app.get("/")
def root():
    return {"message": "MailGenie API is running 🚀"}



app = FastAPI(title="MailGenie")


@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db():
    await close_mongo_connection()


@app.get("/")
async def root():
    return {"status": "MailGenie API running 🚀"}


async def transcribe_audio(audio_url: str) -> str:
    """
    Placeholder for Whisper / Speech-to-Text
    """
    # TODO:
    # 1. Download audio from Twilio
    # 2. Send to Whisper API
    # 3. Return transcribed text
    return "Audio transcription placeholder text"


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()

    from_number = form_data.get("From")          # whatsapp:+91xxxx
    message_body = form_data.get("Body")
    num_media = int(form_data.get("NumMedia", 0))

    media_url = None
    media_type = None

    if num_media > 0:
        media_url = form_data.get("MediaUrl0")
        media_type = form_data.get("MediaContentType0")

    db = get_database()

    # ---------------- User Check ----------------
    user = await db.users.find_one({"phone_number": from_number})

    if not user:
        # Auto-create user (basic version)
        new_user = UserCreate(
            phone_number=from_number,
            email="pending@email.com",
            oauth_tokens=None
        )

        await db.users.insert_one(new_user.model_dump())
        user = await db.users.find_one({"phone_number": from_number})

    # ---------------- Input Handling ----------------
    user_input_text = None

    if media_url and "audio" in (media_type or ""):
        user_input_text = await transcribe_audio(media_url)
    else:
        user_input_text = message_body

    # ---------------- AI Email Generation ----------------
    email_data = generate_email(
        prompt=user_input_text,
        tone="professional",
        language="Hinglish"
    )

    subject = email_data["subject"]
    body = email_data["body"]

    # ---------------- Gmail Draft Creation ----------------
    draft_info = None

    if user.get("oauth_tokens"):
        draft_info = create_draft(
            user_token=user["oauth_tokens"],
            recipient="recipient@example.com",  # later dynamic
            subject=subject,
            body=body
        )

    # ---------------- WhatsApp Reply ----------------
    reply_message = f"""
✉️ *Email Draft Created*

*Subject:* {subject}

*Body:*
{body[:1000]}  # WhatsApp safe limit
"""

    if not user.get("oauth_tokens"):
        reply_message += "\n\n⚠️ Gmail not connected. Please link your Gmail account."

    twiml = MessagingResponse()
    twiml.message(reply_message.strip())

    return Response(
        content=str(twiml),
        media_type="application/xml"
    )