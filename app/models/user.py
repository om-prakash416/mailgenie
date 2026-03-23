from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime
from app.db.database import get_database
from app.models.user import UserCreate

class UserBase(BaseModel):
    phone_number: str = Field(..., example="+919999999999")
    email: EmailStr
    oauth_tokens: Optional[Dict[str, str]] = None


class UserCreate(UserBase):
    pass


class UserInDB(UserBase):
    id: Optional[str] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "phone_number": "+919999999999",
                "email": "user@example.com",
                "oauth_tokens": {
                    "google": "access_token_here",
                    "refresh": "refresh_token_here"
                }
            }
        }


async def create_user(user: UserCreate):
    db = get_database()
    user_dict = user.model_dump()
    result = await db.users.insert_one(user_dict)
    return str(result.inserted_id)