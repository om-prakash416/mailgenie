from fastapi import APIRouter, Request
from fastapi.responses import Response
from typing import Optional

from twilio.twiml.messaging_response import MessagingResponse

from fastapi import APIRouter, Request
from twilio.twiml.messaging_response import MessagingResponse
from app.services.ai_service import generate_email
from app.services.whisper_service import transcribe_audio
from app.db.repositories.conversation_repo import save_message, get_context

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Webhook"])


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Twilio WhatsApp webhook endpoint
    """
    form_data = await request.form()

    # Basic fields
    from_number: Optional[str] = form_data.get("From")
    message_body: Optional[str] = form_data.get("Body")

    # Media handling (audio / image / etc.)
    num_media = int(form_data.get("NumMedia", 0))
    media_url = None
    media_type = None

    if num_media > 0:
        media_url = form_data.get("MediaUrl0")
        media_type = form_data.get("MediaContentType0")

    # --- Business Logic Placeholder ---
    reply_text = "🙏 Thanks for your message!"

    if message_body:
        reply_text = f"📩 You said:\n{message_body}"

    if media_url:
        reply_text += f"\n\n🎧 Media received ({media_type})"

    # Create TwiML response
    twiml_response = MessagingResponse()
    twiml_response.message(reply_text)

    return Response(
        content=str(twiml_response),
        media_type="application/xml"
    )
