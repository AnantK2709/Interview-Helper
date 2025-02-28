from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    is_active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        schema_extra = {
            "example": {
                "id": "60d5ec9af3a66e31084872e9",
                "email": "john@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "created_at": "2023-01-01T00:00:00",
                "is_active": True
            }
        }