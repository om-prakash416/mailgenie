from app.db.database import get_database

async def save_message(phone, role, text):
    db = get_database()
    await db.conversations.update_one(
        {"phone_number": phone},
        {"$push": {"messages": {"role": role, "text": text}}},
        upsert=True
    )

async def get_context(phone, limit=6):
    db = get_database()
    convo = await db.conversations.find_one({"phone_number": phone})
    if not convo:
        return []
    return convo["messages"][-limit:]
