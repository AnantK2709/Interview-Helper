from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .config.db import connect_to_mongo, close_mongo_connection
from .services.webrtc_service import WebRTCService
from .services.question_service import QuestionService
from .services.auth_service import oauth2_scheme, create_access_token, get_password_hash, verify_password
from .models.user import UserCreate, UserResponse
from datetime import timedelta
from typing import List

app = FastAPI(title="Interview Practice API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
webrtc_service = WebRTCService()
question_service = QuestionService()

# Database events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Interview Practice API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    from .config.db import db
    
    # Check if user exists
    existing_user = await db.db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data.pop("password")
    user_data["hashed_password"] = hashed_password
    
    new_user = await db.db.users.insert_one(user_data)
    created_user = await db.db.users.find_one({"_id": new_user.inserted_id})
    
    return UserResponse(**created_user)

@app.get("/questions", response_model=List[dict])
async def get_questions(difficulty: str = "beginner", count: int = 5):
    return question_service.get_questions_by_category(difficulty, count)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await webrtc_service.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process WebRTC signaling data
            await webrtc_service.broadcast({"message": data, "sender": user_id}, [user_id])
    except WebSocketDisconnect:
        webrtc_service.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)