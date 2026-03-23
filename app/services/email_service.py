import base64
from email.mime.text import MIMEText
from typing import List, Dict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# -------- Gmail API Scopes --------
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]


# -------- Helper: Build Gmail Service --------
def get_gmail_service(user_token: dict):
    """
    user_token must contain:
    {
        "access_token": "...",
        "refresh_token": "...",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "...",
        "client_secret": "..."
    }
    """

    creds = Credentials(
        token=user_token.get("access_token"),
        refresh_token=user_token.get("refresh_token"),
        token_uri=user_token.get("token_uri"),
        client_id=user_token.get("client_id"),
        client_secret=user_token.get("client_secret"),
        scopes=SCOPES,
    )

    service = build("gmail", "v1", credentials=creds)
    return service


# -------- Create Gmail Draft --------
def create_draft(
    user_token: dict,
    recipient: str,
    subject: str,
    body: str
) -> Dict:
    """
    Creates a draft email in user's Gmail
    """

    service = get_gmail_service(user_token)

    message = MIMEText(body)
    message["to"] = recipient
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    draft_body = {
        "message": {
            "raw": raw_message
        }
    }

    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=draft_body)
        .execute()
    )

    return {
        "draft_id": draft.get("id"),
        "message_id": draft.get("message", {}).get("id"),
        "status": "draft_created"
    }


# -------- Fetch Unread Emails --------
def get_unread_emails(user_token: dict, max_results: int = 10) -> List[Dict]:
    """
    Fetch unread emails from inbox
    """

    service = get_gmail_service(user_token)

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])
    unread_emails = []

    for msg in messages:
        msg_data = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            )
            .execute()
        )

        headers = msg_data.get("payload", {}).get("headers", [])
        header_map = {h["name"]: h["value"] for h in headers}

        unread_emails.append({
            "id": msg_data.get("id"),
            "thread_id": msg_data.get("threadId"),
            "from": header_map.get("From"),
            "subject": header_map.get("Subject"),
            "date": header_map.get("Date"),
        })

    return unread_emails
